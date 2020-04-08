import matplotlib.pyplot as plt

from .thermoelement import Element
from .thermomodel import Model
from .building import Building


class ThermalProcess:
    """
    Class implements all calculations of thermal processes in house.
    There are three main models of house:
    1. All solar power (with efficient for water solar collector) comes to inside the massive in the house.
    2. All solar power (with efficient for air solar collector) comes to inside the volume in the house.
    3. All solar power comes inside the walls through glass dome.

    """

    def __init__(
            self,
            t_start: float,
            building: Building,
            variant: str = 'all_heat_inside') -> None:
        """
        Initialize item of thermo calculation.
        c - ;
        1,007 - Specific heat capacity of air (wikipedia)
        1,1839 - Density of air (wikipedia)
        There are creating all main thermo elements of the building:
        1. Massive object inside the building (It is model of any massive objects: water boiler, hot floor ,etc.)
        2. Air inside the building.
        3. Walls (without windows).
        4. Windows (if area of windows set in building).
        5. Floor.
        6. Area walls around the massive object.
        7. Outside  - temperature of air around the building.
        8. Floor outside - temperature of air under the floor under the insulation
        9. Glass dome around the building.
        This elements can be combined to three variant (power to massive object, power to air, power to walls).
        dx for non-homogeneous elements is in meters.

        """
        self.count = 0
        self.seconds = 60
        self.building = building
        self.t_start = t_start
        self.sun_power_data = self.building.power_data['summ'].resample('1h').interpolate()
        self.weather_data = self.building.weather_data['temp_air'].resample('1h').interpolate()

        self.alpha_room = 1/0.13
        self.alpha_out = 1/0.04

        self.dx = 0.005     # meters
        self.heat_accumulator_volume = self.building.heat_accumulator['volume']
        if not self.building.heat_accumulator['volume']:
            self.heat_accumulator_volume = (
                    self.building.heat_accumulator['mass']
                    / self.building.get_prop(
                        self.building.heat_accumulator['material'],
                        'density'
                    )
                )

        mass = Element(
            name='mass',
            temp0=self.t_start,
            density=997,
            heat_capacity=4183,
            volume=self.building.heat_accumulator['volume']
        )

        room = Element(
            name='room',
            temp0=self.t_start,
            density=1.27,
            heat_capacity=1007,
            volume=self.building.volume_air_inside,
            area_inside=self.building.floor_area_inside,
            input_alpha=self.alpha_room
        )
        windows = Element(
            name='windows',
            temp0=-5,
            area_inside=self.building.windows['area'],
            input_alpha=1/self.building.windows['therm_r']
        )
        floor = Element(
            name='floor',
            temp0=18,
            area_inside=self.building.floor_area_inside,
            area_outside=self.building.floor_area_outside,
            dx=self.dx,
            thickness=self.building.floor_thickness,
            kappa=self.building.get_prop(
                self.building.floor['material'],
                'kappa'),
            density=self.building.get_prop(
                self.building.floor['material'],
                'density'),
            heat_capacity=self.building.get_prop(
                self.building.floor['material'],
                'heat_capacity'),
            input_alpha=self.alpha_room
        )

        walls = Element(
            name='walls',
            temp0=self.t_start,
            area_inside=self.building.walls_area_inside,
            area_outside=self.building.walls_area_outside,
            dx=self.dx,
            thickness=self.building.wall_thickness,
            kappa=self.building.get_prop(
                self.building.material,
                'kappa'),
            density=self.building.get_prop(
                self.building.material,
                'density'),
            heat_capacity=self.building.get_prop(
                self.building.material,
                'heat_capacity'),
            input_alpha=self.alpha_room
        )
        walls_mass = Element(
            name='walls_mass',
            temp0=self.t_start,
            dx=self.dx,
            area_inside=self.building.area_mass_walls_inside,
            area_outside=self.building.area_mass_walls_outside,
            thickness=self.building.wall_thickness,
            kappa=self.building.get_prop(
                self.building.material,
                'kappa'),
            density=self.building.get_prop(
                self.building.material,
                'density'),
            heat_capacity=self.building.get_prop(
                self.building.material,
                'heat_capacity'),
            input_alpha=self.alpha_room
        )
        outside = Element(
            name='outside',
            temp0=-5,
            area_inside=self.building.walls_area_outside,
            input_alpha=self.alpha_out
        )
        fl_outside = Element(
            name='fl_out',
            temp0=self.building.floor['t_out'],
            area_inside=self.building.floor_area_outside,
            input_alpha=self.alpha_out
        )

        self.model = Model(name=variant)
        if variant == 'power_to_mass':
            mass.branches_loss = [room, floor, walls_mass]
            room.branches_loss = [windows, walls]
            walls.branches_loss = [outside]
            walls_mass.branches_loss = [outside]
            floor.branches_loss = [fl_outside]
            self.model.elements = {
                'mass': mass,
                'room': room,
                'wall': walls,
                'walls_mass': walls_mass,
                'floor': floor,
                'windows': windows,
                'outside': outside,
                'fl_out': fl_outside
            }
            self.model.start_element = mass
            self.model.outside_elements = [outside, fl_outside]
            self.model.plots = [mass, room, walls]
        elif variant == 'power_to_air':
            room.branches_loss = [windows, walls, mass]
            mass.branches_loss = [floor, walls_mass]
            walls.branches_loss = [outside]
            walls_mass.branches_loss = [outside]
            floor.branches_loss = [fl_outside]
            self.model.elements = {
                'mass': mass,
                'room': room,
                'wall': walls,
                'walls_mass': walls_mass,
                'floor': floor,
                'windows': windows,
                'outside': outside,
                'fl_out': fl_outside
            }
            self.model.start_element = room
            self.model.outside_elements = [outside, fl_outside]
            self.model.data_plots = [mass, room, walls]
        elif variant == 'power_to_walls':
            pass

    def run_process(self):
        """
        Start main calculation process.
        In the end of process it show a plots of temperatures
        """
        self.seconds = 60 * 60
        dt = 5
        count_dt = int(self.seconds / dt)
        list_for_plot = []
        for index in self.sun_power_data.index:
            sun = self.sun_power_data[index]
            t_out = self.weather_data[index]
            out_list = self.model.start(
                count=count_dt,
                dt=dt,
                power=sun,
                t_out=t_out
            )

            list_for_plot += out_list

        n = len(self.sun_power_data.index) * count_dt
        print(len(list_for_plot))
        print(n)
        plt.plot(range(n), list_for_plot, lw=2)
        plt.show()
        return

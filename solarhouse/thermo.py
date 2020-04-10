import pandas as pd

from thermoelement import Element
from thermomodel import Model
from building import Building


class ThermalProcess:
    """
    Class implements all calculations of thermal processes in house.
    There are three main models of house:
    1. All solar power (with efficient for water solar collector) comes to inside the massive in the house.
    2. All solar power (with efficient for air solar collector) comes to inside the volume in the house.
    3. All solar power comes inside the walls through glass dome.
    Test variant when all heat comes to mass.
    >>> text = 'o Cube\\n'
    >>> text += 'v 1.000000 1.000000 -1.000000\\n'
    >>> text += 'v 1.000000 0.000000 -1.000000\\n'
    >>> text += 'v 1.000000 1.000000 0.000000\\n'
    >>> text += 'v 1.000000 0.000000 0.000000\\n'
    >>> text += 'v 0.000000 1.000000 -1.000000\\n'
    >>> text += 'v 0.000000 0.000000 -1.000000\\n'
    >>> text += 'v 0.000000 1.000000 0.000000\\n'
    >>> text += 'v 0.000000 0.000000 0.000000\\n'
    >>> text += 's off\\n'
    >>> text += 'f 1/1/1 5/2/1 7/3/1 3/4/1\\n'
    >>> text += 'f 4/5/2 3/6/2 7/7/2 8/8/2\\n'
    >>> text += 'f 8/8/3 7/7/3 5/9/3 6/10/3\\n'
    >>> text += 'f 6/10/4 2/11/4 4/12/4 8/13/4\\n'
    >>> text += 'f 2/14/5 1/15/5 3/16/5 4/17/5\\n'
    >>> text += 'f 6/18/6 5/19/6 1/20/6 2/11/6\\n'
    >>> with open('test_file.obj','a') as file:\
            file.write(text)
    418
    >>> geo = {'latitude': 54.841426, 'longitude': 83.264479}
    >>> vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,1,1],[0,0,1],[1,0,1],[1,1,1]]
    >>> material = {'birch': {\
        'density': 700.0,\
        'transcalency': 0.15,\
        'heat_capacity': 1250.0}}
    >>> b = Building(mesh_file='test_file.obj',\
        geo=geo,\
        wall_thickness=0.3,\
        wall_material='birch',\
        properties_materials=material)
    building ready
    >>> import os
    >>> os.remove('test_file.obj')

    >>>

    """

    def __init__(
            self,
            t_start: float,
            building: Building,
            variant: str = 'heat_to_mass',
            for_plots: list = ['mass',]
        ) -> None:
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
        self.elements_for_plots = for_plots
        self.sun_power_data = self.building.power_data['sum_solar_power'].resample('1h').interpolate()
        self.weather_data = self.building.weather_data['temp_air'].resample('1h').interpolate()

        self.alpha_room = 1/0.13
        self.alpha_out = 1/0.04

        self.dx = 0.005     # meters
        self.heat_accumulator_volume = self.building.heat_accumulator['volume']
        self.heat_accumulator_density = self.building.get_prop(
                        self.building.heat_accumulator['material'],
                        'density'
                    )
        if not self.building.heat_accumulator['volume']:
            self.heat_accumulator_volume = (
                    self.building.heat_accumulator['mass']
                    / self.heat_accumulator_density
                )

        mass = Element(
            name='mass',
            temp0=self.t_start,
            density=self.heat_accumulator_density,
            heat_capacity=4183,
            volume=self.building.heat_accumulator['volume'],
            area_inside=self.building.floor_area_inside,
            input_alpha=self.alpha_room
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

        walls.branches_loss = [outside]
        walls_mass.branches_loss = [outside]
        floor.branches_loss = [fl_outside]

        self.model = Model(name=variant)
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
        self.model.initial_conditions = {
            'mass': self.t_start,
            'room': self.t_start,
            'wall': self.t_start,
            'walls_mass': self.t_start,
            'floor': self.t_start
        }
        self.model.outside_elements = [outside]

        if variant == 'heat_to_mass':
            mass.branches_loss = [room, floor, walls_mass]
            room.branches_loss = [windows, walls]
            self.model.start_element = mass
        elif variant == 'heat_to_air':
            room.branches_loss = [windows, walls, mass]
            mass.branches_loss = [floor, walls_mass]
            self.model.start_element = room
        elif variant == 'heat_to_walls':
            pass

    def run_process(self) -> dict:
        """
        Start main calculation process.
        In the end of process it show a plots of temperatures
        :return: dict data of elements in house for plots.
        """
        self.seconds = 60 * 60
        dt = 5
        count_dt = int(self.seconds / dt)
        pd_for_plot = pd.DataFrame(self.sun_power_data)
        pd_for_plot.insert(1, 'temp_air', self.weather_data)
        dict_for_plot = {}
        self.model.make_init_conditions()
        for name, el in self.model.elements.items():
            print(name, ': ', el.temp)
        for el_name in self.elements_for_plots:
            dict_for_plot.update({el_name: []})
        for index in self.sun_power_data.index:
            # TODO make progress status
            for el in self.elements_for_plots:
                dict_for_plot[el].append(self.model.elements[el].temp)
            sun = self.sun_power_data[index]
            t_out = self.weather_data[index]
            self.model.start(
                count=count_dt,
                dt=dt,
                power=sun,
                t_out=t_out
            )
        count = 1
        for k in dict_for_plot.keys():
            count += 1
            seria = pd.Series(
                dict_for_plot[k],
                self.sun_power_data.index
            )
            pd_for_plot.insert(count, k, seria)
        return pd_for_plot


if __name__ == "__main__":
    import doctest
    doctest.testmod(Element)
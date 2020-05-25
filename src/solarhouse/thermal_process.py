import pandas as pd

from .building import Building
from .thermal_element import ThermalElement
from .thermal_model import ThermalModel


class ThermalProcess:
    """
    Class implements all calculations of thermal processes in a house.
    There are three main models of a house:
    1. All solar power comes into massive body (water tank, concrete
       plate, etc.) in the house with respect to efficient coefficient
       of water solar collector.
    2. All solar power heats up air inside the house with respect
       efficient coefficient of air solar collector.
    3. All solar power heats up walls through a glass dome.
    """

    def __init__(
        self, t_start: float, building: Building, variant: str = "heat_to_mass", for_plots: list = ["mass"],
    ) -> None:
        """
        Initialize item of thermo calculation.
        c - ;
        1,007 - Specific heat capacity of air (wikipedia)
        1,1839 - Density of air (wikipedia)
        There are creating all main thermo elements of the building:
        1. Massive object inside the building
        (It is model of any massive objects: water boiler, hot floor ,etc.)
        2. Air inside the building.
        3. Walls (without windows).
        4. Windows (if area of windows set in building).
        5. Floor.
        6. Area walls around the massive object.
        7. Outside  - temperature of air around the building.
        8. Floor outside - temperature of air under the floor
        under the insulation
        9. Glass dome around the building.
        This elements can be combined to three variant
        (power to massive object, power to air, power to walls).
        dx for non-homogeneous elements is in meters.
        """
        self.count = 0
        self.seconds = 60
        self.building = building
        self.t_start = t_start
        self.elements_for_plots = for_plots
        self.sun_power_data = self.building.power_data["sum_solar_power"].resample("1h").interpolate()
        self.weather_data = self.building.weather_data["temp_air"].resample("1h").interpolate()

        self.alpha_room = 1 / 0.13
        self.alpha_out = 1 / 0.04

        self.dx = 0.005  # meters
        self.heat_accumulator_volume = self.building.heat_accumulator["volume"]
        self.heat_accumulator_density = self.building.get_prop(self.building.heat_accumulator["material"], "density")
        if not self.building.heat_accumulator["volume"]:
            self.heat_accumulator_volume = self.building.heat_accumulator["mass"] / self.heat_accumulator_density

        mass = ThermalElement(
            name="mass",
            temp0=self.t_start,
            density=self.heat_accumulator_density,
            heat_capacity=4183,
            volume=self.building.heat_accumulator["volume"],
            area_inside=self.building.floor_area_inside,
            input_alpha=self.alpha_room,
        )
        room = ThermalElement(
            name="room",
            temp0=self.t_start,
            density=1.27,
            heat_capacity=1007,
            volume=self.building.volume_air_inside,
            area_inside=self.building.floor_area_inside,
            input_alpha=self.alpha_room,
        )
        windows = ThermalElement(
            name="windows",
            temp0=-5,
            area_inside=self.building.windows["area"],
            input_alpha=1 / self.building.windows["therm_r"],
        )
        floor = ThermalElement(
            name="floor",
            temp0=18,
            area_inside=self.building.floor_area_inside,
            area_outside=self.building.floor_area_outside,
            dx=self.dx,
            thickness=self.building.floor_thickness,
            kappa=self.building.get_prop(self.building.floor["material"], "kappa"),
            density=self.building.get_prop(self.building.floor["material"], "density"),
            heat_capacity=self.building.get_prop(self.building.floor["material"], "heat_capacity"),
            input_alpha=self.alpha_room,
        )
        walls = ThermalElement(
            name="walls",
            temp0=self.t_start,
            area_inside=self.building.walls_area_inside,
            area_outside=self.building.walls_area_outside,
            dx=self.dx,
            thickness=self.building.wall_thickness,
            kappa=self.building.get_prop(self.building.material, "kappa"),
            density=self.building.get_prop(self.building.material, "density"),
            heat_capacity=self.building.get_prop(self.building.material, "heat_capacity"),
            input_alpha=self.alpha_room,
        )

        walls_mass = ThermalElement(
            name="walls_mass",
            temp0=self.t_start,
            dx=self.dx,
            area_inside=self.building.area_mass_walls_inside,
            area_outside=self.building.area_mass_walls_outside,
            thickness=self.building.wall_thickness,
            kappa=self.building.get_prop(self.building.material, "kappa"),
            density=self.building.get_prop(self.building.material, "density"),
            heat_capacity=self.building.get_prop(self.building.material, "heat_capacity"),
            input_alpha=self.alpha_room,
        )
        outside = ThermalElement(
            name="outside", temp0=-5, area_inside=self.building.walls_area_outside, input_alpha=self.alpha_out,
        )
        fl_outside = ThermalElement(
            name="fl_out",
            temp0=self.building.floor["t_out"],
            area_inside=self.building.floor_area_outside,
            input_alpha=self.alpha_out,
        )

        walls.branches_loss = [outside]
        walls_mass.branches_loss = [outside]
        floor.branches_loss = [fl_outside]

        self.model = ThermalModel(name=variant)
        self.model.elements = {
            "mass": mass,
            "room": room,
            "wall": walls,
            "walls_mass": walls_mass,
            "floor": floor,
            "windows": windows,
            "outside": outside,
            "fl_out": fl_outside,
        }
        self.model.initial_conditions = {
            "mass": self.t_start,
            "room": self.t_start,
            "wall": self.t_start,
            "walls_mass": self.t_start,
            "floor": self.t_start,
        }
        self.model.outside_elements = [outside]

        if variant == "heat_to_mass":
            mass.branches_loss = [room, floor, walls_mass]
            room.branches_loss = [windows, walls]
            self.model.start_element = mass
        elif variant == "heat_to_air":
            room.branches_loss = [windows, walls, mass]
            mass.branches_loss = [floor, walls_mass]
            self.model.start_element = room
        elif variant == "heat_to_walls":
            pass

    def run_process(self) -> dict:
        """
        Start main calculation process.
        In the end of process it show a plots of temperatures

        :return: dict data of elements in house for plots.
        """
        self.seconds = 60 * 60
        dt = 3
        count_dt = int(self.seconds / dt)
        # pd_for_plot = pd.DataFrame(self.sun_power_data)
        pd_for_plot = pd.DataFrame(self.weather_data)
        # pd_for_plot.insert(1, "temp_air", self.weather_data)
        dict_for_plot = {}
        self.model.make_init_conditions()
        for name, el in self.model.elements.items():
            print(name, ": ", el.temp)
        for el_name in self.elements_for_plots:
            dict_for_plot.update({el_name: []})
        for index in self.sun_power_data.index:
            # TODO make progress status
            for el in self.elements_for_plots:
                dict_for_plot[el].append(self.model.elements[el].temp)
            sun = self.sun_power_data[index]
            t_out = self.weather_data[index]
            self.model.start(count=count_dt, dt=dt, power=sun, t_out=t_out)
        count = 0
        for k in dict_for_plot.keys():
            count += 1
            seria = pd.Series(dict_for_plot[k], self.sun_power_data.index)
            pd_for_plot.insert(count, k, seria)
        return pd_for_plot

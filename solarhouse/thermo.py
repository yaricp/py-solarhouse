from scipy.integrate import *
import numpy as np

from .thermoelement import Element
from .thermomodel import Model


class ThermalProcess:
    """Class implements all calculations of thermal processes."""

    def __init__(
            self,
            t_start,
            building,
            mass_inside=0,
            density_mass=0,
            dict_extra_losses=None,
            variant='all_heat_inside',
            **kwargs):
        """
        Initialize item of thermo calculation.
        c - ;
        1,007 - Specific heat capacity of air (wikipedia)
        1,1839 - Density of air (wikipedia)
        """
        self.count = 0
        self.building = building
        self.T_start = t_start
        #print(building.power_data['summ'])
        #exit(0)
        self.sun_power_data = self.building.power_data['summ'].resample('1h').interpolate()
        self.weather_data = self.building.weather_data['temp_air'].resample('1h').interpolate()

        self.mass_inside = mass_inside
        self.C_mass_inside = 1200
        self.density = density_mass
        self.T_mass = 0
        self.alpha_room = 1/0.13
        self.alpha_out = 1/0.04

        self.dx = 0.005     # meters

        mass = Element(
            name='mass',
            temp0=self.T_start,
            density=997,
            heat_capacity=4183,
            volume=0.5
        )

        room = Element(
            name='room',
            temp0=self.T_start,
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
            dx=0.005,
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
            temp0=self.T_start,
            area_inside=self.building.walls_area_inside,
            area_outside=self.building.walls_area_outside,
            dx=0.005,
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
            temp0=self.T_start,
            dx=0.005,
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
        if variant == 'all_heat_inside':
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
            self.model.outside_elements = [outside,fl_outside]
            self.model.plots = [mass,room,walls]
        elif variant == 'only_sun_power':
            self.update_func = self.heat_sun

    def run_process(self):
        """Start main calculation process."""
        self.seconds = 60*60
        dt = 0.1
        count_dt = int(self.seconds / dt)

        for index in self.sun_power_data.index:
            sun = self.sun_power_data[index]
            self.t_out = self.weather_data[index]
            print('index: ', index)
            print('SUN:', sun)
            print('temp out: ', self.t_out)
            self.model.start(
                count=count_dt,
                dt=dt,
                power=2000,
                t_out=self.t_out
            )
            exit(0)

        return result

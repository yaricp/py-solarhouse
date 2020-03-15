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
        self.sun_power_data = building.power_data['summ'].resample('1h').interpolate()
        self.weather_data = building.weather_data['temp_air'].resample('1h').interpolate()

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
            area_inside=self.building.floor['area_inside'],
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
            area_inside=self.building.floor['area_inside'],
            area_outside=self.building.floor['area_outside'],
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
            area_inside=self.building.floor['area_outside'],
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

        #self.dQx_list = [self.power_inside,
        #            0,
        #            ] + list(np.ones(self.n_points) * 0)

    def __get_H_area_mass(self):
        """

        :return:
        """
        V = self.mass_inside/self.density
        H = V/self.S_floor_inside
        return H * self.perimeter


    def __calc_k(
            self,
            name: str,
            therm_r: float,
            area: float,
            layers: dict = None,
            ) -> float:
        """
        Calculates thermal coefficient of wallings.

        :parameters:
            name - name of element
            therm_r - ready thermal resistance
            area - area of element
            layers - dictionary of element thickness and lambda of layers
        :returns:
            float of coefficient of thermal resistance
        """
        if therm_r:
            return area/therm_r
        a_in = 8.7
        a_out = 23
        if name == 'floor':
            a_out = 6
        elif name == 'ceiling':
            a_out = 12
        therm_r = 1/a_in + 1/a_out
        for row in layers:
            therm_r += row['thickness']/row['lambda']

        return area/therm_r

    def get_sun_power(self, t):
        index = self.sun_power_data.index[int(t)]
        print('Int: ', int(t))
        print('index: ', index)
        print('Sun POwer ', self.sun_power_data[index])
        return self.sun_power_data[index]

    def heat_inside(self, t0, t, *args):
        """
        Calculates PDE for thermal process with all heat inside house.
        dT/dt*c = dQsun/dt + Qinside
                  - (Qwind + Qwall + Qfloor + Qceil)
                  - (Qvent + Qsink)

        dT/dt = 1/c*(dQsun/dt) + Qinside
                    -((Qwind || Swind(dTout/dt - T)/Rwind)
                        + Swall(dTout/dt - T)/Rwall
                        + Sfloor(Toutf - T)/Rfloor
                        + Sceil(dTout/dt - T)/Rceil
                    )
                    -(Qvent + Qsink)
                    )
        dT/dt = 1/c*(dQsun/dt) + Qinside
                    -((Qwind || Kwind(dTout/dt - T)
                        + Kfloor(Toutf - T)
                        + (dTout/dt - T)(Kwall + Kceil)
                    )
                    -(Qextra)
                    )
        T = t0 + 1/c*(dQsun/dt) + Qinside
                    -((Qwind || Kwind(dTout/dt - T)
                        + Kfloor(Toutf - T)
                        + (dTout/dt - T)(Kwall + Kceil)
                    )
                    -(Qextra)
                    )
        """
        dt = 60 * 60
        q_sun = args[0] * dt
        q_inside = self.power_inside * dt
        q_extra = 0
        if self.dict_extra_losses:
            for key, row in self.dict_extra_losses.items():
                q_extra += row * dt
        t_out = args[1]
        delta_t = t0 - t_out
        delta_t_floor = delta_t
        if 'floor' in self.dict_wallings and 't_out' in self.dict_wallings['floor']:
            delta_t_floor = t0 - self.dict_wallings['floor']['t_out']
        q_wind = self.q_windows_losses * dt
        if not self.q_windows_losses:
            q_wind = self.dict_k['windows'] * delta_t
        q_wall_seiling = delta_t * (self.dict_k['walls'] + self.dict_k['ceiling'])
        q_floor = delta_t_floor * self.dict_k['floor']
        result_t = 1/self.c_air_inside * (
            q_sun + q_inside
            - (q_wind + q_wall_seiling + q_floor)
            - q_extra
        )
        print('1/c_air: ',1/self.c_air_inside)
        print('q_res: ', (
            q_sun + q_inside
            - (q_wind + q_wall_seiling + q_floor)
            - q_extra
        ))
        return result_t

    def calcT_Q(self, q0, T10, T20, iterator, branch):
        """

        :param q0:
        :param T10:
        :param T20:
        :param iterator:
        :return:
        """

        dS = self.calc_dict[branch]['dS'][iterator]
        dCm = self.calc_dict[branch]['dCm'][iterator]
        qr = round(dS*(T10 - T20), 3)
        qc = q0 - qr
        if dCm == 0:
            dTdt = 0
        else:
            dTdt = qc / dCm
        T11 = T10 + dTdt
        #if iterator <= 2 and (branch == 'floor' or branch == 'room-walls'):
        #    print('branch: ', branch)
        #    print('q0: ', q0)
        #    print('T11: ', T11)
        return T11, qr

    def prepare_chain(self, direction):
        """

        :param direction:
        :return:
        """
        dRwall = self.dx / self.kappa
        if direction == 'room-walls':
            Tx_list = np.ones(self.n_points + 1) * self.T_start
            dS_walls_list = []
            dCm_walls_list = []
            for i in range(0, self.n_points):
                dS = self.S_walls_inside + (i * self.dx * self.K_walls)
                dCm = dS * self.dx * self.density_walls * self.heat_capacity_walls
                dS_walls_list.append(dS/dRwall)
                dCm_walls_list.append(dCm)
            dS_list = ([self.S_floor_inside/self.R_room,
                       self.S_walls_inside/self.R_room]
                        + dS_walls_list
                        + [self.S_walls_outside/self.R_out])
            dCm_list = [self.mass_inside * self.C_mass_inside,
                        self.mass_air_room * self.c_air_room,
                        ] + dCm_walls_list
        elif direction == 'floor':
            Tx_list = list(np.ones(self.n_points) * self.T_start)
            dS_walls_list = []
            dCm_walls_list = []
            for i in range(0, self.n_points):
                dS = self.S_floor_inside + (i * self.dx * self.K_walls)
                dCm = dS * self.dx * self.density_walls * self.heat_capacity_walls
                dS_walls_list.append(dS / dRwall)
                dCm_walls_list.append(dCm)
            dS_list = ([self.S_floor_inside/self.R_room]
                       + dS_walls_list
                       + [self.S_floor_outside/self.R_out_floor])
            dCm_list = [self.mass_inside * self.C_mass_inside,
                        ] + dCm_walls_list
        elif direction == 'mass-walls':
            Tx_list = np.ones(self.n_points) * self.T_start
            dS_walls_list = []
            dCm_walls_list = []
            for i in range(0, self.n_points):
                dS = self.H_area
                dCm = dS * self.dx * self.density_walls * self.heat_capacity_walls
                dS_walls_list.append(dS/dRwall)
                dCm_walls_list.append(dCm)
            dS_list = ([self.H_area/self.R_room]
                        + dS_walls_list
                        + [self.H_area/self.R_out])
            dCm_list = [self.mass_inside * self.C_mass_inside,
                        ] + dCm_walls_list
        elif direction == 'windows':
            Tx_list = [self.t_out]
            dS_list = [self.building.windows['area']/self.building.windows['therm_r']]
            dCm_list = [0]

        self.calc_dict.update({direction: {
            'Tx': Tx_list,
            'dS': dS_list,
            'dCm': dCm_list,
        }})

        return



    def run_heat_in_mass(self, sun, temp_out):
        """

        :return:
        """

        for t in range(0, self.seconds):
            q_enter = sun + self.power_inside
            # qc = q_enter - get_all_q_loss(dT_list[0], loss_node[0])
            # dTdt = round(qc / Cmx_list[0], 3)
            # dT_list[0] += dTdt
            for b, row in self.calc_dict.items():
                #print('  start chain ', b)
                T20 = row['Tx'][0]
                #print('  T20: ', T20)
                dS = row['dS'][0]
                #print('  dS: ', dS)
                qr = round(dS * (self.T_mass - T20), 3)
                #print('  qr: ', qr)
                qc -= qr
                #print('  qc: ', qc)
                q0 = qr
                n = len(row['Tx'])
                #print('  q0 enter in chain: ', q0)
                for x in range(0, n):
                    T10 = row['Tx'][x]
                    if x < (n - 1):
                        T20 = row['Tx'][x + 1]
                    else:
                        T20 = temp_out + (self.R_out * q1) / self.S_walls_outside
                    T11, q1 = self.calcT_Q(q0, T10, T20, x, b)
                    row['Tx'][x] = round(T11,3)
                    q0 = q1
            dTdt = round(qc / (self.mass_inside * self.C_mass_inside), 3)
            self.T_mass = self.T_mass + dTdt
            #print('  Tmass: ',self.T_mass)
            #if t == 120:
        print('room-walls', self.calc_dict['room-walls']['Tx'])
        print('---------------------------------------')
        print('mass-walls', self.calc_dict['mass-walls']['Tx'])
        print('---------------------------------------')
        print('floor', self.calc_dict['floor']['Tx'])
        print('---------------------------------------')
        return

    def run_process(self):
        """Start main calculation process."""
        '''
        self.T_mass = self.T_start
        branches = ['floor', 'room-walls', 'mass-walls']
        nodes = {1:['floor', 'room-walls', 'mass-walls'],
                 2:['windows']}
        for b in branches:
            self.prepare_chain(b)
        '''
        self.seconds = 60*60

        for index in self.sun_power_data.index:
            sun = self.sun_power_data[index]
            self.t_out = self.weather_data[index]
            print('index: ', index)
            print('SUN:', sun)
            print('temp out: ', self.t_out)
            self.model.start(
                seconds=self.seconds,
                power=sun,
                t_out=self.t_out
            )
            exit(0)
            #result = self.run_heat_in_mass(sun, self.t_out)

        return result

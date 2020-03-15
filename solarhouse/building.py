
import math
import datetime
import pandas as pd
import numpy as np

from trimesh import triangles

import pvlib
from pvlib.pvsystem import PVSystem
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP


from trimesh import geometry, load

from settings import *

temperature_model_parameters = TEMPERATURE_MODEL_PARAMETERS['sapm']['open_rack_glass_glass']

properties_materials = {'cob': {
                                'transcalency': 0.04,
                                'heat_capacity': 450.0,
                                'density': 450.0
                                }, 
                        }


class Building:
    """
    Class implements methods for work with buildings for which calculate sun energy.
    Test for cube 1x1x1 meter :
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
        wall_thickness=1,\
        wall_material='birch',\
        properties_materials=material)
    building ready
    >>> import os
    >>> os.remove('test_file.obj')
    >>> b.wall_thickness
    0.5
    >>> b.mass_walls
    700.0
    >>> b.mass
    700.0
    >>> b.mesh.center_mass
    array([0. , 0. , 0.5])
    >>> b.calc_power_lost_face(1, 1)
    0.2864
    >>> b.calc_power_lost(19)
    1.7184
    >>> b.calc_temp_in_house(1000, 0)
    >>> round(b.current_temp, 4)
    19.9314
    >>> import datetime, pytz
    >>> date = datetime.datetime(day=22, month=6, year=2020)
    >>> timezone = pytz.timezone('Asia/Novosibirsk')
    >>> import sun
    >>> sun = sun.Sun(geo=geo, timezone=timezone)
    >>> sun_vector = sun.change_position(date, 12, 0)
    >>> sun_power = sun.power_on_meter_from_pysolar
    >>> b.calc_power_sun_on_face(sun, sun.vector, 1) == sun_power * (b.efficiency/100)
    True
    >>> from trimesh import geometry
    >>> sun_angle = geometry.vector_angle(((0, 0, 1), sun_vector))
    >>> power_on_face = sun_power * math.cos(sun_angle)
    >>> b.calc_power_sun_on_face(sun,[0, 0, 1],1) == power_on_face * (b.efficiency/100)
    True

    """

    def __init__(
                self,
                mesh_file: str,
                geo: dict,
                wall_material: str = 'cob',
                wall_thickness: float = 0.3,
                start_temp_in: float = 20,
                power_heat_inside: float = 0,
                efficiency: float = 60,
                effective_angle: float = 65,
                cover_material: str = None,
                **kwargs
                ) -> None:
        """ Initialize object of class Building. """
        self.mesh = load(mesh_file)
        self.__mesh_inside = None
        # print(dir(self.mesh))
        # exit(0)
        if not self.mesh.is_watertight:
            raise Exception(
                'Mesh is not watertight',
                'Error')
        self.geo = geo
        self.material = wall_material
        self.wall_thickness = wall_thickness
        self.current_temp = start_temp_in
        # power_heat_inside kWatt
        self.power_heat_inside = power_heat_inside * 1000
        self.efficiency = efficiency
        self.effective_angle = effective_angle
        self.cover_material = cover_material
        self.dict_properties_materials = properties_materials
        self.therm_r = kwargs.get('therm_r', None)
        self.wall_layers = kwargs.get('wall_layers', None)
        self.dict_power_inside = kwargs.get('dict_power_inside', None)
        dict_properties_materials = kwargs.get('properties_materials', None)
        if dict_properties_materials:
            self.dict_properties_materials.update(dict_properties_materials)
        self.dict_mass_inside = kwargs.get('dict_mass_inside', None)
        if self.dict_mass_inside:
            self.__check_materials()
        self.ventilation_losses = kwargs.get('ventilation_losses', 0)
        self.heat_accumulator = kwargs.get('heat_accumulator', {
            'volume': 1,
            'material': 'water',
            'mass': 996,
            'heat_capacity': 4136,
            'density': 996
        })
        self.windows = kwargs.get('windows', {
            'therm_r': 0,
            'losses': 0,
            'area': 0,
            })
        self.floor = kwargs.get('floor', {
            'therm_r': 0,
            'area': 0,
            'layers': []
            })
        self.ceiling = kwargs.get('ceiling', {
            'therm_r': 0,
            'area': 0,
            'layers': []
            })
        self.extra_losses = kwargs.get('extra_losses', {})

        self.__centring()

        self.__correct_wall_thickness()
        #self.__calc_mass_walls()

        self.weather_data = None
        self.power_data = None
        self.power_data_by_days = None
        self.location = Location(
            latitude=geo['latitude'],
            longitude=geo['longitude'])
        self.pv = PVSystem(
            surface_tilt=45,
            surface_azimuth=180,
            module_parameters={'pdc0': 240, 'gamma_pdc': -0.004},
            inverter_parameters={'pdc0': 240},
            temperature_model_parameters=temperature_model_parameters,
        )
        self.mc = ModelChain(
            self.pv,
            self.location,
            aoi_model='no_loss',
            spectral_model='no_loss')

        print('building ready')
        return

    def __check_materials(self) -> None :
        """ Check is the materials in dict of materilas. """
        for k_m in self.dict_mass_inside.keys():
            if k_m not in self.dict_properties_materials.keys():
                raise Exception(
                    "Unknown material!",
                    "Error"
                    )

    def __correct_wall_thickness(self) -> None:
        """ Method for correct the wall thickness. """
        for base in self.mesh.bounding_box.primitive.extents:
            scale_factor = (base - self.wall_thickness*2)/base
            if scale_factor < 0:
                self.wall_thickness = min(
                    self.mesh.bounding_box.primitive.extents)/2
        return
        
    def __centring(self):
        """ Method for centring of the mesh. """
        where_move = self.mesh.center_mass * -1.0
        self.mesh.apply_translation(where_move)
        where_move = self.mesh.center_mass
        z_move = abs(self.mesh.center_mass[2] - self.mesh.bounds[0][2])
        where_move[2] = z_move
        self.mesh.apply_translation(where_move)
        return
    '''    
    def __calc_mass_walls(self) -> None:
        """ Calculate mass of the walls of building. """
        
        wall_volume = self.mesh.volume

            self.volume_air_inside = self.mesh_inside.volume
            wall_volume = self.mesh.volume - self.mesh_inside.volume
        density = self.dict_properties_materials[self.material]['density']
        self.mass_walls = (
                wall_volume * density
                - self.windows['area'] * self.wall_thickness * density
                - self.floor['area_outside'] * self.wall_thickness * density
                - self.ceiling['area'] * self.wall_thickness * density
                )
        return
    '''

    @property
    def mesh_inside(self):
        factors = []
        if self.__mesh_inside:
            return self.__mesh_inside
        for base in self.mesh.bounding_box.primitive.extents:
            scale_factor = (base - self.wall_thickness*2)/base
            factors.append(scale_factor)
        if factors != [0.0, 0.0, 0.0]:
            matrix = np.diag(factors + [1.0])
            self.__mesh_inside = self.mesh.copy().apply_transform(matrix)
        return self.__mesh_inside

    @property
    def walls_area_inside(self):
        area = (
            self.mesh_inside.area
            - self.windows['area']
            - self.floor['area_inside']
        )
        if area < 0:
            raise Exception('Area is null')
        return area

    @property
    def walls_area_outside(self):
        area = (
            self.mesh.area
            - self.windows['area']
            - self.floor['area_outside']
        )
        if area < 0:
            raise Exception('Area is null')
        return area
    
    @property
    def face_normals(self) -> list:
        return self.mesh.face_normals
        
    @property
    def face_areas(self) -> list:
        return self.mesh.area_faces

    @property
    def volume_air_inside(self) -> float:
        """"""
        if self.heat_accumulator['volume']:
            return (
                    self.mesh_inside.volume
                    - self.heat_accumulator['volume']
            )
        if self.heat_accumulator['mass'] and self.heat_accumulator['density']:
            mass_volume = self.heat_accumulator['mass'] * self.heat_accumulator['density']
        else:
            mass_volume = self.get_prop(
                self.heat_accumulator['material'],
                'density'
            ) * self.heat_accumulator['mass']
        return self.mesh_inside.volume - mass_volume

    @property
    def floor_thickness(self) -> float:
        """"""
        if 'thickness' in self.floor and self.floor['thickness']:
            return self.floor['thickness']
        return self.wall_thickness


    def get_perimeter(self, where):
        pass
        return

        
    def get_efficient_angle(self, reflect_material: dict = None) -> float:
        """ Get angle for material. """
        ang = reflect_material[self.material]
        return ang
        
    def calc_reflect_power(
            self,
            power: float,
            sun_ang: float,
            cover_material: str = 'polycarbonat') -> float:
        """
        Calculates
        power of reflection based on :
        https://majetok.blogspot.ru/2014/05/vid-na-teplicu.html.
        Returns: float of power of the reflection of material.

        """
        #    dict_kr_mat = {'polycarbonat':1.585, 
        #                  'glass':1.4}
        #    dict_ki_mat = {'polycarbonat':0.82, 
        #                    'glass':0.86}
        table_kr_mat = {'polycarbonat': {
                                        40: 0.04,
                                        50: 0.06,
                                        60: 0.1,
                                        70: 0.18,
                                        80: 0.4,
                                        90: 1},
                        }
        kr = 1
        for k, v in table_kr_mat[cover_material].items():
            if math.degrees(sun_ang) <= k:
                kr = v
                continue
        refl_power = power * kr
        return refl_power

    def get_pv_power_face(
            self,
            face_tilt,
            face_azimuth,
            face_area):
        """ Get Irradiation from PVLIB. """
        self.pv.surface_tilt = face_tilt
        self.pv.surface_azimuth = face_azimuth
        self.mc.run_model(self.weather_data)
        return self.mc.effective_irradiance * face_area * (self.efficiency/100)

    '''
    def calc_power_sun_on_face(
            self,
            face_normal: list,
            face_area: float) -> float:
        """
        Calculates the sun power on the face of building.
        Returns: Float value of the sun power.
        """
        sun_power_efficient = 0
        sun_ang = geometry.vector_angle((face_normal, sun.vector))
        if math.degrees(sun_ang) < self.effective_angle and sun.altitude > 0:
            sun_power_on_face = sun.power_on_meter_from_pysolar * \
                                face_area * math.cos(sun_ang)
            sun_power = sun_power_on_face   # - self.calc_reflect_power(sun_power, sun_ang)
            sun_power_efficient = sun_power * (self.efficiency/100)
        return sun_power_efficient

    def get_dict_power_by_hours(self) -> tuple:
        """
        Calculates the power of sun on all faces of the building.
        :return: tuple of follow
         - max power of all faces
         - index of the face with max power
         - count of the faces which takes sun power in this time
         - sum power from all faces in this time
        """
        for h, row in self.weather_data.items():
            outdict = self.calc_sun_power_on_faces()
            self.power_data.update({h: outdict})

        return
    '''

    def projection_on_flat(self, vector) -> tuple:
        """ get vector what is projection vector on the flat plane. """
        u = vector
        n = np.array([0, 0, 1])
        n_norm = np.sqrt(sum(n ** 2))
        proj_of_u_on_n = (np.dot(u, n) / n_norm ** 2) * n
        return u - proj_of_u_on_n

    def calc_sun_power_on_faces(self) -> None:
        """
        Calculates the power of sun on all faces of the building.
        :returns: self
            changed self.power_data, self.power_data_by_days
        """
        dict_temp_data = {}
        # self.power_data = pd.DataFrame(index=self.weather_data.index)
        face_indexes = []
        count_faces = 0

        if count_faces >= COUNT_FACES_FOR_PARALLEL_CALC:
            # TODO Start parallels calc in actors model
            pass
        else:
            index = 0
            for face in self.mesh.faces:
                tri = [self.mesh.vertices[i].tolist() for i in face]
                face_area = triangles.area((tri, ))
                face_normal = triangles.normals((tri, ))[0][0]
                # TODO make next step in actor
                # sun_ang = geometry.vector_angle((face_normal, sun.vector))
                # if math.degrees(sun_ang) < self.effective_angle and sun.altitude > 0:

                face_tilt = geometry.vector_angle((face_normal, (0, 0, 1)))
                face_normal_projection = self.projection_on_flat(face_normal)
                face_azimuth = geometry.vector_angle((face_normal_projection, (0, 1, 0)))
                sun_power_face = self.get_pv_power_face(
                    face_tilt,
                    face_azimuth,
                    face_area,
                )
                face_seria = pd.Series(
                    sun_power_face,
                    index=self.weather_data.index,
                    )
                dict_temp_data.update({index: face_seria})
                face_indexes.append(index)
                index += 1
        self.power_data = pd.DataFrame(dict_temp_data)
        fields = list(self.power_data)
        self.power_data['summ'] = self.power_data[fields].sum(axis=1)
        self.power_data['maximum'] = self.power_data[fields].max(axis=1)
        self.power_data['ind_face'] = self.power_data[fields].idxmax(axis=1)
        self.power_data_by_days = self.power_data['summ'].resample('1D').mean()
        return

    def get_prop(self, material, prop):
        """"""
        if not material in self.dict_properties_materials:
            material = self.material
        if prop == "kappa":
            return 1/self.dict_properties_materials[material][prop]
        return self.dict_properties_materials[material][prop]

    def prepare_dict_wallings(self):
        """Prepares dictionary layers of wallings."""

        if not self.therm_r and not self.wall_layers:
            self.wall_layers = [{
                'thickness': self.wall_thickness,
                'c': self.dict_properties_materials[self.material]['heat_capacity'],
                'lambda': self.dict_properties_materials[self.material]['transcalency'],
                'mass': self.mass_walls
                }]
        dict_walls = {
            'area': self.walls_area,
            'therm_r': self.therm_r,
            'layers': self.wall_layers
            }
        if (
                self.floor['area']
                and ('therm_r' not in self.floor or not self.floor['therm_r'])
                and not self.floor['layers']
            ):
            mat = self.floor['material']
            if not mat:
                mat = self.material
            self.floor['layers'] = [{
                'thickness': self.wall_thickness,
                'lambda': self.dict_properties_materials[mat]['transcalency'],
                'c': self.dict_properties_materials[mat]['heat_capacity'],
                'mass': (
                    self.floor['area']
                    * self.floor['thickness']
                    * self.dict_properties_materials[mat]['density']
                    )
                }]
        if (
                self.ceiling['area']
                and ('therm_r' not in self.ceiling or not self.ceiling['therm_r'])
                and not self.ceiling['layers']
            ):
            mat = self.ceiling['material']
            if not mat:
                mat = self.material
            self.ceiling['layers'] = [{
                    'thickness': self.wall_thickness,
                    'lambda': self.dict_properties_materials[mat]['transcalency'],
                    'c': self.dict_properties_materials[mat]['heat_capacity'],
                    'mass': (
                        self.ceiling['area']
                        * self.ceiling['thickness']
                        * self.dict_properties_materials[mat]['density']
                    )
                }]
        dict_wallings = {
            'windows': self.windows,
            'floor': self.floor,
            'ceiling': self.ceiling,
            'walls': dict_walls,
            }
        return dict_wallings


if __name__ == "__main__":
    import doctest
    doctest.testmod()
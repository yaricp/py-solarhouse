import math

import numpy as np
import pandas as pd
from pvlib.location import Location
from pvlib.modelchain import ModelChain
from pvlib.pvsystem import PVSystem
from pvlib.temperature import TEMPERATURE_MODEL_PARAMETERS
from trimesh import geometry, load, triangles

from . import settings

temp_model_pars = TEMPERATURE_MODEL_PARAMETERS["sapm"]["open_rack_glass_glass"]

properties_materials = {
    "adobe": {"transcalency": 0.04, "heat_capacity": 450.0, "density": 450.0},
    "water": {"transcalency": 0.599, "heat_capacity": 4182, "density": 998.29},
    "birch": {"transcalency": 0.15, "heat_capacity": 1250.0, "density": 700.0},
}


class Building:
    """
    Class implements methods for work with buildings for which calculate
    sun energy.
    Example: create building and test some it`s parameters.

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
    >>> vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[0,1,1],[0,0,1],[1,0,1],\
    [1,1,1]]
    >>> material = {'birch': {\
        'density': 700.0,\
        'transcalency': 0.15,\
        'heat_capacity': 1250.0}}
    >>> b = Building(mesh_file='test_file.obj',\
        geo=geo,\
        wall_thickness=0.3,\
        wall_material='birch',\
        properties_materials=material)
    >>> import os
    >>> os.remove('test_file.obj')
    >>> b.wall_thickness
    0.3
    >>> b.mesh.area
    6.0
    >>> round(b.mesh_inside.volume, 3)
    0.064
    >>> b.mesh.center_mass
    array([0. , 0. , 0.5])
    >>> b.floor_area_outside
    1.0
    >>> round(b.floor_area_inside, 3)
    0.16
    >>> b.windows['area']
    0.0
    >>> b.windows['area'] = 0.5
    >>> b.walls_area_outside
    4.5
    >>> round(b.walls_area_inside, 3)
    0.3
    >>> b.heat_accumulator['mass'] = 1
    >>> b.heat_accumulator['density'] = 1000
    >>> b.get_perimeter_floor('inside')
    1.6
    >>> round(b.area_mass_walls_inside, 2)
    0.2
    >>> round(b.volume_air_inside, 3)
    0.044
    >>> b.get_perimeter_floor('outside')
    4.0
    >>> round(b.area_mass_walls_outside, 3)
    1.7
    >>> import datetime, pytz
    >>> date = datetime.datetime(day=22, month=6, year=2020)

    """

    thermal_elements = [
        "mass",
        "room",
        "wall",
        "walls_mass",
        "floor",
        "windows",
        "outside",
        "fl_out",
    ]

    def __init__(
        self,
        mesh_file: str,
        geo: dict,
        wall_material: str = "adobe",
        wall_thickness: float = 0.3,
        start_temp_in: float = 20,
        power_heat_inside: float = 0,
        efficiency: float = 60,
        cover_material: str = None,
        heat_accumulator: dict = {"volume": 0.02, "material": "water"},
        **kwargs
    ) -> None:
        """ Initialize object of class Building. """
        self.mesh = load(mesh_file)
        self.__mesh_inside = None
        if not self.mesh.is_watertight:
            raise Exception("Mesh is not watertight", "Error")
        self.material = wall_material
        self.wall_thickness = wall_thickness
        self.current_temp = start_temp_in
        # power_heat_inside kWatt
        self.power_heat_inside = power_heat_inside * 1000
        self.efficiency = efficiency
        self.cover_material = cover_material
        self.dict_properties_materials = properties_materials
        self.wall_layers = kwargs.get("wall_layers", None)
        self.dict_power_inside = kwargs.get("dict_power_inside", None)
        self.dict_properties_materials = kwargs.get("properties_materials", properties_materials)
        self.ventilation_losses = kwargs.get("ventilation_losses", 0)
        self.heat_accumulator = heat_accumulator
        self.windows = kwargs.get("windows", {"therm_r": 0.0, "losses": 0.0, "area": 0.0})
        self.floor = kwargs.get("floor", {"material": self.material, "therm_r": 0, "area": 0, "layers": []})
        self.ceiling = kwargs.get("ceiling", {"material": self.material, "therm_r": 0, "area": 0, "layers": []},)
        self.extra_losses = kwargs.get("extra_losses", {})

        self.__centring()

        self.__correct_wall_thickness()

        self.weather_data = {}
        self.power_data = {}
        self.power_data_by_days = None
        self.location = Location(latitude=geo["latitude"], longitude=geo["longitude"],)
        self.pv = PVSystem(
            surface_tilt=45,
            surface_azimuth=180,
            module_parameters={"pdc0": 240, "gamma_pdc": -0.004},
            inverter_parameters={"pdc0": 240},
            temperature_model_parameters=temp_model_pars,
        )
        self.mc = ModelChain(self.pv, self.location, aoi_model="no_loss", spectral_model="no_loss")
        return

    def __correct_wall_thickness(self) -> None:
        """ Method for correct the wall thickness. """
        for base in self.mesh.bounding_box.primitive.extents:
            scale_factor = (base - self.wall_thickness * 2) / base
            if scale_factor < 0:
                self.wall_thickness = min(self.mesh.bounding_box.primitive.extents) / 2
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

    @property
    def mesh_inside(self):
        """Get mesh of inside walls and floor of the house"""
        factors = []
        if self.__mesh_inside:
            return self.__mesh_inside
        for base in self.mesh.bounding_box.primitive.extents:
            scale_factor = (base - self.wall_thickness * 2) / base
            factors.append(scale_factor)
        if factors != [0.0, 0.0, 0.0]:
            matrix = np.diag(factors + [1.0])
            self.__mesh_inside = self.mesh.copy().apply_transform(matrix)
        return self.__mesh_inside

    @property
    def walls_area_inside(self):
        """Calculates area of walls inside the house"""
        area = self.mesh_inside.area - self.windows["area"] - self.floor_area_inside
        if area < 0:
            raise Exception("Area is null")
        return area

    @property
    def walls_area_outside(self):
        """Calculates area of walls outside the house"""
        area = self.mesh.area - self.windows["area"] - self.floor_area_outside
        if area < 0:
            raise Exception("Area is null")
        return area

    @property
    def face_normals(self) -> list:
        return self.mesh.face_normals

    @property
    def face_areas(self) -> list:
        return self.mesh.area_faces

    @property
    def volume_air_inside(self) -> float:
        """Calculates volume of the air inside the house"""
        return self.mesh_inside.volume - self.heat_accumulator_volume

    @property
    def floor_thickness(self) -> float:
        """Get floor thickness"""
        if "thickness" in self.floor and self.floor["thickness"]:
            return self.floor["thickness"]
        return self.wall_thickness

    @property
    def heat_accumulator_volume(self):
        """Get volume of heat accumulator"""
        if "volume" in self.heat_accumulator and self.heat_accumulator["volume"]:
            return self.heat_accumulator["volume"]
        if "material" in self.heat_accumulator and self.heat_accumulator["material"]:
            return self.get_prop(self.heat_accumulator["material"], "density") * self.heat_accumulator["mass"]
        return self.heat_accumulator["mass"] / self.heat_accumulator["density"]

    @property
    def area_mass_walls_inside(self) -> float:
        """Calculates area of the walls around the heat accumulator
        inside of the house."""
        if not self.heat_accumulator:
            return 0
        p = self.get_perimeter_floor("inside")
        h = self.heat_accumulator_volume / self.floor_area_inside
        return p * h

    @property
    def area_mass_walls_outside(self) -> float:
        """Calculates area of the walls around the heat accumulator outside of
         the house."""
        p = self.get_perimeter_floor("outside")
        h = self.heat_accumulator_volume / self.floor_area_inside
        th = self.wall_thickness
        if "thickness" in self.floor and self.floor["thickness"]:
            th = self.floor["thickness"]
        return (h + th) * p

    @property
    def floor_area_outside(self) -> float:
        """Calculates area floor outside of the house"""
        area = 0
        for norm, area_f in zip(self.mesh.face_normals, self.mesh.area_faces):
            if norm[2] == -1:
                area += area_f
        return area

    @property
    def floor_area_inside(self) -> float:
        """Calculates area floor inside of the house"""
        area = 0
        for norm, area_f in zip(self.mesh_inside.face_normals, self.mesh_inside.area_faces):
            if norm[2] == -1:
                area += area_f
        return area

    def get_perimeter_floor(self, where: str) -> float:
        """
        Calculate perimeter of floor

        :param where: 'inside' or 'outside'
        :return:
            float value of perimeter
        """
        if where == "outside":
            return self.mesh.section(plane_origin=self.mesh.bounds[0], plane_normal=[0, 0, 1]).length
        else:
            return self.mesh_inside.section(plane_origin=self.mesh_inside.bounds[0], plane_normal=[0, 0, 1]).length

    def get_efficient_angle(self, reflect_material: dict = None) -> float:
        """ Get angle for material. """
        ang = reflect_material[self.material]
        return ang

    def calc_reflect_power(self, power: float, sun_ang: float, cover_material: str = "polycarbonat") -> float:
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
        table_kr_mat = {
            "polycarbonat": {40: 0.04, 50: 0.06, 60: 0.1, 70: 0.18, 80: 0.4, 90: 1},
        }
        kr = 1
        for k, v in table_kr_mat[cover_material].items():
            if math.degrees(sun_ang) <= k:
                kr = v
                continue
        refl_power = power * kr
        return refl_power

    def get_pv_power_face(self, face_tilt: float, face_azimuth: float, face_area: float) -> float:
        """
        Get Irradiation from PVLIB.

        :param face_tilt: angle between normal of face and horizontal plane
        :param face_azimuth: angle between normal of face and north direction
        :param face_area: float value of area of face
        :return: pandas DataFrame with sun power of current period.
        """
        self.pv.surface_tilt = face_tilt
        self.pv.surface_azimuth = face_azimuth
        self.mc.run_model(self.weather_data)
        return self.mc.effective_irradiance * face_area * (self.efficiency / 100)

    def projection_on_flat(self, vector: tuple) -> tuple:
        """ get vector what is projection vector on the flat plane. """
        u = vector
        n = np.array([0, 0, 1])
        n_norm = np.sqrt(sum(n ** 2))
        proj_of_u_on_n = (np.dot(u, n) / n_norm ** 2) * n
        return u - proj_of_u_on_n

    def calc_sun_power_on_faces(self) -> None:
        """
        Calculates the power of sun on all faces of the building.

        :return: self
            changed self.power_data, self.power_data_by_days
        """
        dict_temp_data = {}
        face_indexes = []
        count_faces = 0

        if count_faces >= settings.COUNT_FACES_FOR_PARALLEL_CALC:
            # TODO Start parallels calc in actors model
            pass
        else:
            index = 0
            for face in self.mesh.faces:
                tri = [self.mesh.vertices[i].tolist() for i in face]
                face_area = triangles.area((tri,))
                face_normal = triangles.normals((tri,))[0][0]
                face_tilt = geometry.vector_angle((face_normal, (0, 0, 1)))
                face_normal_projection = self.projection_on_flat(face_normal)
                face_azimuth = geometry.vector_angle((face_normal_projection, (0, 1, 0)))
                sun_power_face = self.get_pv_power_face(face_tilt, face_azimuth, face_area,)
                face_seria = pd.Series(sun_power_face, index=self.weather_data.index,)
                dict_temp_data.update({index: face_seria})
                face_indexes.append(index)
                index += 1
        self.power_data = pd.DataFrame(dict_temp_data)
        fields = list(self.power_data)
        self.power_data["sum_solar_power"] = self.power_data[fields].sum(axis=1)
        self.power_data["maximum_solar_power"] = self.power_data[fields].max(axis=1)
        self.power_data["ind_face"] = self.power_data[fields].idxmax(axis=1)
        self.power_data_by_days = self.power_data["sum_solar_power"].resample("1D").mean()
        return

    def get_prop(self, material: str, prop: str) -> float:
        """
        Retrive a value of property for some materials.

        :param material: string of name material
        :param prop: string of name property
        :return: float of value property
        """
        if material not in self.dict_properties_materials:
            material = self.material
        if prop == "kappa":
            return self.dict_properties_materials[material]["transcalency"]
        return self.dict_properties_materials[material][prop]


if __name__ == "__main__":
    import doctest

    doctest.testmod()

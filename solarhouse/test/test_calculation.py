import os

from calculation import Calculation
from test_building import create_file_mesh, remove_file_mesh


def create_calc():
    create_file_mesh()
    c = Calculation(
        tz='Asia/Novosibirsk',
        path_file_object='solarhouse/test/test_file.obj',
        geo={
            'latitude': 54.841426,
            'longitude': 83.264479},
        wall_material='cob',
        wall_thickness=0.1,
        start_temp_in=15.0,
        power_heat_inside=500,
        efficiency_collector=0.6,
    )
    remove_file_mesh()
    return c


c = create_calc()

from building import Building
from calculation import Calculation


def test_create_calculation(mesh_file_path):
    geo = {
        'latitude': 54.841426,
        'longitude': 83.264479,
    }
    c = Calculation(
        tz='Asia/Novosibirsk',
        geo=geo,
        building=Building(
            mesh_file=mesh_file_path,
            geo=geo,
            wall_material='adobe',
            wall_thickness=0.1,
            start_temp_in=15.0,
            power_heat_inside=500,
            efficiency=0.6,
        ),
        building_mesh_file_path=mesh_file_path,
        wall_material='adobe',
        wall_thickness=0.1,
        start_temp_in=15.0,
        power_heat_inside=500,
        efficiency_collector=0.6,
    )

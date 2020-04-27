from calculation import Calculation


def test_create_calculation(mesh_file_path):
    c = Calculation(
        tz='Asia/Novosibirsk',
        path_file_object=mesh_file_path,
        geo={
            'latitude': 54.841426,
            'longitude': 83.264479},
        wall_material='adobe',
        wall_thickness=0.1,
        start_temp_in=15.0,
        power_heat_inside=500,
        efficiency_collector=0.6,
    )

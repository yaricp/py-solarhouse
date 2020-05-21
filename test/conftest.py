import os

import pytest

from building import Building


@pytest.fixture(scope="session")
def mesh_file_path():
    text = """
o Cube
v 1.000000 1.000000 -1.000000
v 1.000000 0.000000 -1.000000
v 1.000000 1.000000 0.000000
v 1.000000 0.000000 0.000000
v 0.000000 1.000000 -1.000000
v 0.000000 0.000000 -1.000000
v 0.000000 1.000000 0.000000
v 0.000000 0.000000 0.000000
s off
f 1/1/1 5/2/1 7/3/1 3/4/1
f 4/5/2 3/6/2 7/7/2 8/8/2
f 8/8/3 7/7/3 5/9/3 6/10/3
f 6/10/4 2/11/4 4/12/4 8/13/4
f 2/14/5 1/15/5 3/16/5 4/17/5
f 6/18/6 5/19/6 1/20/6 2/11/6
"""
    output_file_path = 'test/test_file.obj'

    with open(output_file_path, 'w') as file:
        file.write(text)

    yield output_file_path

    os.remove(output_file_path)


@pytest.fixture(scope="session")
def building(mesh_file_path):
    """Create building for tests"""
    geo = {
        'latitude': 54.841426,
        'longitude': 83.264479,
    }
    material = {
        'birch': {
            'density': 700.0,
            'transcalency': 0.15,
            'heat_capacity': 1250.0
        },
    }
    ret = Building(
        mesh_file=mesh_file_path,
        geo=geo,
        wall_thickness=0.3,
        wall_material='birch',
        properties_materials=material
    )
    return ret

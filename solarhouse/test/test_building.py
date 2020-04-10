import os
import datetime
import pytz

from building import Building

text = 'o Cube\n'
text += 'v 1.000000 1.000000 -1.000000\n'
text += 'v 1.000000 0.000000 -1.000000\n'
text += 'v 1.000000 1.000000 0.000000\n'
text += 'v 1.000000 0.000000 0.000000\n'
text += 'v 0.000000 1.000000 -1.000000\n'
text += 'v 0.000000 0.000000 -1.000000\n'
text += 'v 0.000000 1.000000 0.000000\n'
text += 'v 0.000000 0.000000 0.000000\n'
text += 's off\n'
text += 'f 1/1/1 5/2/1 7/3/1 3/4/1\n'
text += 'f 4/5/2 3/6/2 7/7/2 8/8/2\n'
text += 'f 8/8/3 7/7/3 5/9/3 6/10/3\n'
text += 'f 6/10/4 2/11/4 4/12/4 8/13/4\n'
text += 'f 2/14/5 1/15/5 3/16/5 4/17/5\n'
text += 'f 6/18/6 5/19/6 1/20/6 2/11/6\n'
with open('solarhouse/test/test_file.obj', 'a') as file:
    file.write(text)
geo = {'latitude': 54.841426, 'longitude': 83.264479}
vertices = [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0], [0, 1, 1], [0, 0, 1], [1, 0, 1], [1, 1, 1]]
material = {
    'birch': {
        'density': 700.0,
        'transcalency': 0.15,
        'heat_capacity': 1250.0
        }
    }
b = Building(
    mesh_file='solarhouse/test/test_file.obj',
    geo=geo,
    wall_thickness=0.3,
    wall_material='birch',
    properties_materials=material
)
os.remove('solarhouse/test/test_file.obj')
assert b.wall_thickness == 0.3
assert b.mesh.area == 6.0
assert round(b.mesh_inside.volume, 3) == 0.064
assert b.mesh.center_mass[0] == 0.0
assert b.mesh.center_mass[1] == 0.0
assert b.mesh.center_mass[2] == 0.5
assert b.floor_area_outside == 1.0
assert round(b.floor_area_inside, 3) == 0.16
assert b.windows['area'] == 0.0
b.windows['area'] = 0.5
assert b.walls_area_outside == 4.5
assert round(b.walls_area_inside, 3) == 0.3
b.heat_accumulator['mass'] = 1
b.heat_accumulator['density'] = 1000
assert b.get_perimeter_floor('inside') == 1.6
assert round(b.area_mass_walls_inside, 2) == 0.01
assert round(b.volume_air_inside, 3) == 0.063
assert b.get_perimeter_floor('outside') == 4.0
assert round(b.area_mass_walls_outside, 3) == 1.225

date = datetime.datetime(day=22, month=6, year=2020)
import os
import shutil

import export as ex
from calculation import Calculation

from test_building import create_file_mesh, remove_file_mesh


def test_main():
    tz = 'Asia/Novosibirsk'
    file_path = create_file_mesh()
    geo = {'latitude': 54.841426,
           'longitude': 83.264479}
    output = 'solarhouse/test/output2'
    calc = Calculation(
        tz,
        file_path,
        geo,
        wall_material='cob',
        wall_thickness=0.3,
        start_temp_in=20.0,
        power_heat_inside=0.0,
        efficiency_collector=75,
        path_output_file=output,
        mass_inside=0,
        heat_accumulator={'volume': 0.02, 'material': 'water'},
        windows={'area': 0.3, 'therm_r': 5.0},
        floor={'area': 1.0, 'material': 'cob', 'thickness': 0.2, 't_out': 4.0},
    )
    remove_file_mesh()
    calc_id = calc.id
    dataf = calc.start(date=22, with_weather=True)
    os.mkdir(output)
    os.mkdir(os.path.join(output, calc_id))

    assert os.path.exists(os.path.join(output, calc_id))

    ex.as_file(dataf, 'csv', os.path.join(output, calc_id))
    ex.as_html(dataf, os.path.join(output, calc_id))

    assert os.path.exists(os.path.join(output, calc_id, 'data.csv'))
    assert os.path.exists(os.path.join(output, calc_id, 'plots.html'))

    with open(os.path.join(output, calc_id, 'data.csv'), 'r') as file:
        text_f = file.read()
        assert text_f.find('sum_solar_power') != -1
        assert text_f.find('temp_air') != -1
        assert text_f.find('mass') != -1
        assert text_f.find('room') != -1

    shutil.rmtree(output)

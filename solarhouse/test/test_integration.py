import os
import filecmp
import shutil

import export as ex
from calculation import Calculation


def test_main(mesh_file_path):
    tz = 'Asia/Novosibirsk'
    file_path = mesh_file_path
    geo = {'latitude': 54.841426, 'longitude': 83.264479}
    output = 'solarhouse/test/output2'
    calc = Calculation(
        tz,
        file_path,
        geo,
        wall_material='adobe',
        wall_thickness=0.3,
        start_temp_in=20.0,
        power_heat_inside=0.0,
        efficiency_collector=75,
        path_output_file=output,
        heat_accumulator={'volume': 0.032, 'material': 'water'},
        windows={'area': 0.3, 'therm_r': 5.0},
        floor={'area': 1.0, 'material': 'adobe', 'thickness': 0.2, 't_out': 4.0},
    )
    calc_id = calc.id
    dataf = calc.start(date=22, month=12, year=2019, with_weather=False)
    os.mkdir(output)
    os.mkdir(os.path.join(output, calc_id))

    assert os.path.exists(os.path.join(output, calc_id))

    ex.as_file(dataf, 'csv', os.path.join(output, calc_id))
    ex.as_html(dataf, os.path.join(output, calc_id))

    assert os.path.exists(os.path.join(output, calc_id, 'data.csv'))
    assert os.path.exists(os.path.join(output, calc_id, 'plots.html'))

    res_file = os.path.join(output, calc_id, 'data.csv')
    with open(res_file, 'r') as file:
        text_f = file.read()
        assert text_f.find('sum_solar_power') != -1
        assert text_f.find('temp_air') != -1
        assert text_f.find('mass') != -1
        assert text_f.find('room') != -1

    ref_file = os.path.join('solarhouse/test/ref_files', 'data.csv')
    filecmp.cmp(res_file, ref_file)
    shutil.rmtree(output)

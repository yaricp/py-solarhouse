import os
import filecmp

from solarhouse.building import Building
from solarhouse.calculation import Calculation
import solarhouse.export as export


def test_main(mesh_file_path, tmpdir):
    tz = "Asia/Novosibirsk"
    geo = {
        "latitude": 54.841426,
        "longitude": 83.264479,
    }
    calc = Calculation(
        tz=tz,
        geo=geo,
        building=Building(
            mesh_file=mesh_file_path,
            geo=geo,
            wall_material="adobe",
            wall_thickness=0.3,
            start_temp_in=20.0,
            power_heat_inside=0.0,
            efficiency=75,  # TODO: percents or fractions of 1?
            heat_accumulator={"volume": 0.032, "material": "water"},
            windows={"area": 0.3, "therm_r": 5.0},
            floor={"area": 1.0, "material": "adobe", "thickness": 0.2, "t_out": 4.0},
        ),
    )
    data_frame = calc.compute(date=22, month=12, year=2019, with_weather=False)

    output_dir = tmpdir

    export.as_file(data_frame, "csv", output_dir)
    res_file = os.path.join(output_dir, "data.csv")
    ref_res_file = os.path.join("test/ref_files", "data.csv")
    assert filecmp.cmp(res_file, ref_res_file)

    export.as_html(data_frame, output_dir)
    assert os.path.exists(os.path.join(output_dir, "plots.html"))

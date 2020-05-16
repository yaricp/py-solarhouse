import os, datetime

import settings
from solarhouse.building import Building
from solarhouse.calculation import Calculation
import solarhouse.export as export


def main():
    calc = Calculation(
        tz=settings.TZ,
        geo=settings.GEO,
        building=Building(
            mesh_file=settings.PATH_FILE_OBJECT,
            geo=settings.GEO,
            wall_material=settings.WALL_MATERIAL,
            wall_thickness=settings.WALL_THICKNESS,
            start_temp_in=settings.TEMPERATURE_START,
            power_heat_inside=settings.POWER_HEAT_INSIDE,
            efficiency=settings.EFF,
            heat_accumulator={
                'volume': 0.02,
                'material': 'water',
            },
            windows={
                'area': 0.3,
                'therm_r': 5.0,
            },
            floor={
                'area': 1.0,
                'material': 'adobe',
                'thickness': 0.2,
                't_out': 4.0,
            },
        ),
        building_mesh_file_path=settings.PATH_FILE_OBJECT,
        wall_material=settings.WALL_MATERIAL,
        wall_thickness=settings.WALL_THICKNESS,
        start_temp_in=settings.TEMPERATURE_START,
        power_heat_inside=settings.POWER_HEAT_INSIDE,
        efficiency_collector=settings.EFF,
        heat_accumulator={
            'volume': 0.02,
            'material': 'water',
        },
        windows={
            'area': 0.3,
            'therm_r': 5.0,
        },
        floor={
            'area': 1.0,
            'material': 'adobe',
            'thickness': 0.2,
            't_out': 4.0,
        },
    )

    data_frame = calc.compute(date=22, month=12, year=2019, with_weather=False)

    output_dir = os.path.join(settings.PATH_OUTPUT, calc.id)
    os.makedirs(output_dir, exist_ok=True)

    csv_file_path = export.as_file(data_frame, 'csv', output_dir)
    export.as_html(data_frame, output_dir)
   
    with open(csv_file_path, 'r') as file:
        print(file.read())


if __name__ == "__main__":
    main()

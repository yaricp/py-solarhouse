import os, datetime


from settings import *
import solarhouse.export as ex
from solarhouse.calculation import Calculation


def main():
    calc = Calculation(
                        TZ, 
                        PATH_FILE_OBJECT,
                        GEO, 
                        WALL_MATERIAL,
                        WALL_THICKNESS, 
                        TEMPERATURE_START, 
                        POWER_HEAT_INSIDE,
                        EFF,
                        heat_accumulator={'volume': 0.02, 'material': 'water'},
                        windows={'area': 0.3, 'therm_r': 5.0},
                        floor={'area': 1.0, 'material': 'adobe', 'thickness': 0.2, 't_out': 4.0},
                    )
    date = datetime.datetime(day=22, month=7, year=2019)
    calc_id = calc.id
    if not os.path.exists(os.path.join(PATH_OUTPUT, calc_id)):
        os.mkdir(os.path.join(PATH_OUTPUT, calc_id))
    data_frame = calc.compute(date=22, month=12, year=2019, with_weather=False)
    ex.as_file(data_frame, 'csv', os.path.join(PATH_OUTPUT, calc_id))
    ex.as_html(data_frame, os.path.join(PATH_OUTPUT, calc_id))
   
    with open(os.path.join(PATH_OUTPUT, calc_id, 'data.csv'), 'r') as file:
        print(file.read())


main()

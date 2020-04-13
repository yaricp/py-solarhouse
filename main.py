import os, datetime

from settings import *
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
                        PATH_OUTPUT,
                        mass_inside=0)
    date = datetime.datetime(day=22, month=7, year=2019)
    calc_id = calc.id

    calc.start(date=22, with_weather=True)
    calc.export()
    calc.create_html()
   
    with open(os.path.join(PATH_OUTPUT, calc_id, 'data.csv'), 'r') as file:
        print(file.read())


main()

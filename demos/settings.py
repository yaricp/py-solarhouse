import os
import pathlib


_this_dir = pathlib.Path(__file__).parent.absolute()

PATH_FILE_OBJECT = os.path.join(_this_dir, 'files/cube.stl')
TIME_TICK = 1    #1 hours
WALL_THICKNESS = 0.3
TEMPERATURE_START = 20  #celcium
POWER_HEAT_INSIDE = 0   #kWtt
MASS_INSIDE = 500   #kg
PATH_FILE_TEMPERATURE_OUTSIDE_FILE = os.path.join(_this_dir, 'files/temp_table.csv')
PATH_EXPORT_THERMO_RESULT_FILE = os.path.join(_this_dir, 'files/results.csv')
SPACE_POWER_ON_METER = 1000
WALL_MATERIAL = 'adobe'
EFF = 75        #in percents 
EFF_ANG = 85.0
GEO = {
    'latitude': 54.841426,
    'longitude': 83.264479,
}
TZ = 'Asia/Novosibirsk'
COUNT_FACES_FOR_PARALLEL_CALC = 1000
PATH_OUTPUT = os.path.join(_this_dir, 'output')

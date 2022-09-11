![Image tests](https://travis-ci.com/yaricp/py-solarhouse.svg?branch=master)

[![Documentation](https://readthedocs.org/projects/solarhouse/badge/?version=latest&style=flat)](https://py-solarhouse.readthedocs.io/en/latest/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## About
This project allows for calculation of amount of solar energy one can collect from faces of a house as well as changes of the energy over the heating season in a given geographical location.

A mesh file (.stl or .obj) with a model of a house is required. Heat-related parameters of a house are specified in a separated configuration file. After calculation is over, user gets plots and tabulated values of temperatures of elements inside house.

Model of thermal processes in the house are calculated via models described in the section [Thermal theory](https://solarhouse.readthedocs.io/en/latest/thermal_theory.html) in the project's [documentation](https://solarhouse.readthedocs.io).

By changing different parameters of the house one can carry out calculations for every configuration and to choose the best combination of parameters to save energy for heating.

Credits:
* faces of mesh are processed by [PyMesh](https://pymesh.readthedocs.io/en/latest/)  library;
* to calculate solar power on each face of a house with respect to different tilts and azimuths, [PVLIB](https://pvlib-python.readthedocs.io/en/stable/) is used; this library makes it possible to account for real weather when calculating power input.

## Version
0.0.4

## Documentation

[Documentation](https://solarhouse.readthedocs.io).

## Dependencies

    numpy
    scipy
    trimesh
    pvlib
    pandas
    matplotlib
    mpld3
    shapely
    jinja2
    netCDF4
    siphon
    tables

## Installation

From PyPI:

    $ pip install solarhouse
    
From GitHub:

    $ git clone https://github.com/yaricp/py-solarhouse.git
    $ cd py-solarhouse
    $ ./install.sh

## Usage

First of all you need to create a mesh with shape of a house. For example, it can be created online in [SketchUp](https://app.sketchup.com) for free (registration is required).

Alternatively, the mesh can be created in any 3D editor which can produce .obj and .stl files, e.g., [Blender](https://www.blender.org/).

A ready mesh is put .files/  folder.

file main.py:

    import os

    import uuid

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
                    'volume': 0.032,
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
                        )
        data_frame = calc.compute(date=22, month=12, year=2019, with_weather=False)
        calc_id = str(uuid.uuid4())
        output_dir = os.path.join(settings.PATH_OUTPUT, calc_id)
        os.makedirs(output_dir, exist_ok=True)
        csv_file_path = export.as_file(data_frame, 'csv', output_dir)
        export.as_html(data_frame, output_dir)

    if __name__ == "__main__":
        main()


file settings.py:


    import os
    import pathlib


    _this_dir = pathlib.Path(__file__).parent.absolute()

    PATH_FILE_OBJECT = os.path.join(_this_dir, 'files/cube.obj')
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

All parameters of a house (mesh, thickness of wall, material of walls and etc.) sets in file settings.py

After that you can start calculation:

    $ python3 main.py

As a result you a spreadsheet and a graph as two files in folder `output/<calc_id>`: `data.csv` and `plot.html`.

## Author
Yaroslav Pisarev (yaricp@gmail.com).

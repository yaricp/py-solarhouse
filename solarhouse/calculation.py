import os
import datetime
import calendar
import pytz
import matplotlib.pyplot as plt
import mpld3
import uuid
import csv

import pandas as pd
from pvlib.forecast import GFS

from building import Building
from thermo import ThermalProcess


class Calculation:
    """
    Class implements methods for calculate of the solar power
    what you can take on faces of the building.
    As result you can get html page with graphics.
    Also you can export data in file CSV or JSON.
    """
    
    def __init__(
                self,
                tz,
                path_file_object,
                geo,
                wall_material,
                wall_thickness, 
                start_temp_in,
                power_heat_inside, 
                efficiency_collector,
                efficient_angle_collector=70,
                path_output_file='output',
                **kwargs
                ):
        """ Initialize object for calculate sun power. """
        self.id = str(uuid.uuid4())
        self.progress = 0
        self.output_file_dir = os.path.join(path_output_file, self.id)
        self.geo = geo
        if not os.path.exists(self.output_file_dir):
            os.makedirs(self.output_file_dir)
        self.timezone = pytz.timezone(tz)
        self.tz = pytz.timezone(tz)
        self.pd_data_for_export = None
        self.headers = {
            'power': ['day', 'sum_watt_hour'],
            'temperature': ['day', 'temp in', 'temp out']
        }
        self.building = Building(
            path_file_object,
            geo,
            wall_material,
            wall_thickness,
            start_temp_in,
            power_heat_inside,
            efficiency_collector,
            efficient_angle_collector,
            windows={'area': 12.0, 'therm_r': 0.5},
            heat_accumulator={'volume': 1.0, 'material': 'water'},
            floor={'t_out': 4.0,
                   'material': wall_material,
                   'layers': [{
                    'thickness': 0.1,
                    'lambda':0.04,
                    'c': 4500,
                    'mass': 2000,
                }]
            }
        )

    def __get_weather(self, start, end):
        """
        Get weather data for period.
        :param start: - pd.Timestamp, begin of period
        :param end: - pd.Timestamp, end of period
        :return: pd.DataFrame,
            Column names are: ``ghi, dni, dhi``
        """
        fx_model = GFS()
        print('START: ', start)
        print('END: ', end)
        return fx_model.get_processed_data(
            self.geo['latitude'],
            self.geo['longitude'],
            start,
            end)

    def __get_clear_sky(self, start, end, model='ineichen'):
        """
        Get sun data of irradiation of sun without weather.
        :param start: - pd.Timestamp, begin of period
        :param end: - pd.Timestamp, end of period
        :param model: - str, The clear sky model to use. Must be one of
            'ineichen', 'haurwitz', 'simplified_solis'.
        :return: pd.DataFrame,
            Column names are: ``ghi, dni, dhi``
        """
        period = pd.date_range(start=start, end=end, freq='1h', tz=self.tz)
        return self.building.location.get_clearsky(period,model=model)

    def start(
            self,
            date=None,
            month=None,
            year=None,
            period=None,
            with_weather=True
            ):
        """ Start calculate for day, month or year. """
        get_weather = self.__get_clear_sky
        if with_weather:
            get_weather = self.__get_weather
        if year:
            start = pd.Timestamp(year, tz=self.tz)
            end = start + pd.Timedelta(years=1)
        elif month:
            year = datetime.datetime.now().year
            start = pd.Timestamp(datetime.datetime(year=year, month=month), tz=self.tz)
            end = start + pd.Timedelta(months=1)
        elif date:
            start = pd.Timestamp(date, tz=self.tz)
            end = start + pd.Timedelta(days=7)
        elif period:
            start = pd.Timestamp(period[0], tz=self.tz)
            end = pd.Timestamp(period[1], tz=self.tz)
        else:
            date = datetime.datetime.now()
            start = pd.Timestamp(date, tz=self.tz)
            end = start + pd.Timedelta(days=7)
        self.building.weather_data = get_weather(start, end)
        self.building.calc_sun_power_on_faces()
        thermal_process = ThermalProcess(
            t_start=20,
            building=self.building,
            variant='heat_to_mass',
            for_plots=['mass', 'room']
        )
        self.pd_data_for_export = thermal_process.run_process()
        return

    def export(self, type_file: str = 'csv', path: str = '') -> None:
        """ Export results to file. """
        if not path:
            path = self.output_file_dir
        file_path = os.path.join(path, 'data.%s' % type_file)
        with open(file_path, "w", newline='') as file:
            if type_file == 'csv':
                file.write(self.pd_data_for_export.to_csv())
            else:
                file.write(self.pd_data_for_export.to_json(orient='split'))
                pass
        return

    def create_html(self) -> None:
        """ Create HTML page with graphics. """
        fig = plt.figure()
        ax = fig.subplots()
        ax.plot(self.pd_data_for_export)
        file_obj = os.path.join(self.output_file_dir, 'plots.html')
        mpld3.save_html(fig, file_obj)
        return


if __name__ == "__main__":
    import doctest
    doctest.testmod()
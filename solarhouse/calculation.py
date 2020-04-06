import os
import datetime
import calendar
import pytz
import matplotlib.pyplot as plt
import mpld3
import uuid
import csv

import pandas as pd
from pvlib.forecast import GFS, NAM, NDFD, HRRR, RAP

#from .sun import Sun
from .building import Building
from .thermo import ThermalProcess


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
        #self.sun = Sun(geo, tz, with_weather)
        self.tz = pytz.timezone(tz)
        self.day_dict_powers = {}
        self.month_dict_powers = {}
        self.year_dict_powers = {}
        self.day_dict_temp = {}
        self.month_dict_temp = {}
        self.year_dict_temp = {}
        self.sum_watt_hour = 0
        self.dict_data_for_export = {
            'power': {
                'day': self.day_dict_powers,
                'month': self.month_dict_powers,
                'year': self.year_dict_powers
            },
            'temperature': {
                'day': self.day_dict_temp,
                'month': self.month_dict_temp,
                'year': self.year_dict_temp
            }
        }
        self.headers = {
            'power': ['day', 'sum_watt_hour'],
            'temperature': ['day', 'temp in', 'temp out']
        }
        self.dict_temperature_outside = kwargs.get('temperature_outside', None)
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
            heat_accumulator={'volume': 1.0, 'density': 996.0},
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

    def __calc_day(self, date: datetime = datetime.datetime.now()):
        """ Calculate sun power and temperature inside building. """
        temperature_out = -20
        hour_powers_tuple = self.building.get_dict_power_by_hours()
        self.sum_watt_hour += hour_powers_tuple[3]
        # TODO get temperature_out = archive_temperatures[year][month][date]
        power_house_heat_lost = self.building.calc_power_lost()
        self.building.calc_temp_in_house(
            power_house_heat_lost,
            hour_powers_tuple[3])
        temperature_in = self.building.current_temp
        if hour_powers_tuple != (0, 0, 0, 0.0):
            self.day_dict_powers.update({h: [
                hour_powers_tuple,
                self.sum_watt_hour
            ]})
            self.day_dict_temp.update({h: [
                0,
                (temperature_in, temperature_out)
            ]})

        return

    def __calc_day_old(
            self,
            date: datetime = datetime.datetime.now(),
            month: int = datetime.datetime.now().month,
            year: int = datetime.datetime.now().year
            ) -> None:
        """ Calculate sun power and temperature inside building. """
        temperature_out = -20
        if self.dict_temperature_outside:
            temperature_out = self.dict_temperature_outside[date]
        for h in range(0, 24):
            self.progress = h * 100 // 24
            self.sun.change_position(date, h, 0)
            hour_powers_tuple = self.building.calc_sun_power_on_faces(self.sun)
            self.sum_watt_hour += hour_powers_tuple[3]
            # TODO get temperature_out = archive_temperatures[year][month][date]
            power_house_heat_lost = self.building.calc_power_lost(temperature_out)
            self.building.calc_temp_in_house(
                                            power_house_heat_lost,
                                            hour_powers_tuple[3])
            temperature_in = self.building.current_temp
            if hour_powers_tuple != (0, 0, 0, 0.0):
                self.day_dict_powers.update({h: [
                    hour_powers_tuple,
                    self.sum_watt_hour
                ]})
                self.day_dict_temp.update({h: [
                    0,
                    (temperature_in, temperature_out)
                ]})
        return
        
    def __calc_month(
            self,
            month: int = datetime.datetime.now().month,
            year: int = datetime.datetime.now().year
            ) -> None:
        """ Calculate power by day in month. """
        days = calendar.monthrange(year, month)[1]
        for d in range(1, days):
            self.progress = d * 100 // days
            date = datetime.datetime(day=d, month=month, year=year)
            self.__calc_day(date, month, year)
            self.month_dict_powers.update({d: [
                self.day_dict_powers,
                self.sum_watt_hour,
            ]})
            self.month_dict_temp.update({d: [
                self.day_dict_temp,
                (self.building.current_temp, 0)
            ]})
        return
            
    def __calc_year(
            self,
            year=datetime.datetime.now().year
            ) -> None:
        """ Calculate powers by months in year. """
        for m in range(1, 12):
            self.progress = m*100//12
            self.__calc_month(m, year)
            self.year_dict_powers.update({m: [
                self.month_dict_powers,
                self.sum_watt_hour,
            ]})
            self.year_dict_temp.update({m: [
                self.month_dict_temp,
                (self.building.current_temp, 0)
            ]})
        return

    def __get_weather(self, start, end):
        """
        Get weather data for period.
        :parameters:
            start - pd.Timestamp, begin of period
            end - pd.Timestamp, end of period
        :retuns: pd.DataFrame,
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
        :parameters:
            start - pd.Timestamp, begin of period
            end - pd.Timestamp, end of period
            model - str, The clear sky model to use. Must be one of
            'ineichen', 'haurwitz', 'simplified_solis'.
        :retuns: pd.DataFrame,
            Column names are: ``ghi, dni, dhi``
        """
        period = pd.date_range(start=start, end=end, freq='1h', tz=self.tz)
        return self.building.location.get_clearsky(period,model=model)

        
    def create_html(self, what: str, period: str) -> None:
        """ Create HTML page with graphics. """
        dict_data = self.dict_data_for_export[what][period]
        data = [item[1] for k, item in dict_data.items()]
        fig = plt.figure()
        ax = fig.subplots()
        ax.plot(data)
        fileobj = os.path.join(self.output_file_dir, '%s.html' % what)
        mpld3.save_html(fig, fileobj)
        return

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
        #print(start)
        #print(end)
        self.building.weather_data = get_weather(start, end)
        print(self.building.weather_data.index)
        self.building.calc_sun_power_on_faces()
        #dict_walling = self.building.prepare_dict_wallings()
        t_proc = ThermalProcess(20, self.building)
        t_proc.run_process()
        #
        # self.building.calc_temp_in_house()
        return

    def export(
            self,
            what: str,
            period: str,
            type_file: str = 'csv',
            path: str = '') -> None:
        """ Export results to file. """
        if what not in ['temperature', 'power']:
            return
        if not path:
            path = self.output_file_dir
        header = self.headers[what]
        header[0] = period
        dict_data = self.dict_data_for_export[what][period]
        file_path = os.path.join(path, '%ss.%s' % (what, type_file))
        with open(file_path, "w", newline='') as file:
            if type_file == 'csv':
                writer = csv.writer(file, delimiter=',')
                writer.writerow(header)
                for k, data in dict_data.items():
                    print(data[1])
                    line = [k, data[1]]
                    writer.writerow(line)
            else:
                # write json
                pass

        return

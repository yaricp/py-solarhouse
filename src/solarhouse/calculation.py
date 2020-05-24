import datetime

import pandas as pd
import pytz
from pvlib.forecast import GFS

from .building import Building
from .helpers import prepare_period
from .thermal_process import ThermalProcess


class Calculation:
    """
    Class implements methods for calculate of the solar power
    what you can take on faces of the building.
    As result you can get html page with graphics.
    Also you can export data in file CSV or JSON.
    """

    def __init__(self, tz: str, geo: dict, building: Building):
        """ Initialize object for calculate sun power. """
        self.progress = 0
        self.geo = geo
        self.tz = pytz.timezone(tz)
        self.pd_data_for_export = None
        self.building = building

    def compute(
        self,
        date: datetime.datetime = None,
        month: datetime.datetime = None,
        year: datetime.datetime = None,
        period: tuple = None,
        with_weather: bool = True,
    ) -> None:
        """ proxy method for prepare period and calculations. """
        start, end = prepare_period(tz=self.tz, date=date, month=month, year=year, period=period)
        return self.start_calculation(start, end, with_weather=with_weather)

    def __get_weather(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        """
        Get weather data for period.
        :param start: - pd.Timestamp, begin of period
        :param end: - pd.Timestamp, end of period
        :return: pd.DataFrame,
            Column names are: ``ghi, dni, dhi``
        """
        fx_model = GFS()
        return fx_model.get_processed_data(self.geo["latitude"], self.geo["longitude"], start, end)

    def __get_clear_sky(self, start: pd.Timestamp, end: pd.Timestamp, model: str = "ineichen") -> pd.DataFrame:
        """
        Get sun data of irradiation of sun without weather.
        :param start: - pd.Timestamp, begin of period
        :param end: - pd.Timestamp, end of period
        :param model: - str, The clear sky model to use. Must be one of
            'ineichen', 'haurwitz', 'simplified_solis'.
        :return: pd.DataFrame,
            Column names are: ``ghi, dni, dhi``
        """
        period = pd.date_range(start=start, end=end, freq="1h", tz=self.tz)
        return self.building.location.get_clearsky(period, model=model)

    def start_calculation(self, start: pd.Timestamp, end: pd.Timestamp, with_weather: bool = True) -> None:
        """ Start calculations. """
        get_weather = self.__get_clear_sky
        if with_weather:
            get_weather = self.__get_weather
        self.building.weather_data = get_weather(start, end)
        self.building.calc_sun_power_on_faces()
        thermal_process = ThermalProcess(
            t_start=20, building=self.building, variant="heat_to_mass", for_plots=["mass", "room"],
        )
        self.pd_data_for_export = thermal_process.run_process()
        return self.pd_data_for_export


if __name__ == "__main__":
    import doctest

    doctest.testmod()

import datetime
import math
import pytz

# TODO try to use https://github.com/santoshphilip/pyephem_sunpath
from pysolar.solar import get_altitude, get_azimuth
from pysolar import radiation


class Sun:
    """
    Class implements methods for work with sun object.

    """
    
    def __init__(
            self,
            geo: dict,
            timezone: str,
            **kwargs
            ) -> None:
        """ Initialize object of the sun. """
        self.vector = (1, 0, 0)
        self.geo = geo
        self.timezone = pytz.timezone(timezone)
        self.datetime = datetime.datetime(
                                        day=1,
                                        month=1,
                                        year=2019,
                                        hour=1,
                                        minute=1,
                                        tzinfo=self.timezone)
        self.dict_loss_clouds = kwargs.get('dict_loss_clouds', None)

    def get_data_irradiations(self, period):
        """get sun irradiations or """


'''
    @property
    def altitude(self):
        return get_altitude(
                        self.geo['latitude'], 
                        self.geo['longitude'], 
                        self.datetime)
       
    @property
    def azimuth(self):
        return get_azimuth(
                        self.geo['latitude'], 
                        self.geo['longitude'], 
                        self.datetime)

    def change_position(
            self,
            date: datetime.date,
            hour: int,
            minute: int) -> None:
        """
        Changes position of the sun object.
        Calculates vector of the sun object.
        :param date: date of the sun position
        :param hour: hour of the sun position
        :param minute: minute of the sun position
        :return: None
        """
        self.datetime = datetime.datetime(
                                year=date.year, 
                                month=date.month, 
                                day=date.day, 
                                hour=hour, 
                                minute=minute, 
                                tzinfo=self.timezone
                                )
        altitude = math.radians(self.altitude)
        azimuth = math.radians(-self.azimuth)
        loc_z = math.sin(altitude)
        hyp = math.cos(altitude)
        loc_y = hyp*math.cos(azimuth)
        loc_x = -hyp*math.sin(azimuth)
        self.vector = (loc_x, loc_y, loc_z)
        return
    
    @property
    def power_on_meter_from_pysolar(self) -> float:
        """
        Get power of sun from the module radiation of pysolar package.
        Returns: float of the power of the sun
        """
        power = radiation.get_radiation_direct(self.datetime, self.altitude)
        return power

    def get_clouds(self) -> None:
        """ Get lost power of the solar power in the clouds"""
        # TODO find and realize calculate lost power in clouds
        pass
        return
'''
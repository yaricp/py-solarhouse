import datetime

import pandas as pd


def prepare_period(
    tz,
    date: datetime.datetime = None,
    month: datetime.datetime = None,
    year: datetime.datetime = None,
    period: tuple = None,
) -> tuple:
    """
    Prepare period for retrive data of wheather and calculate sun power.
    :param tz:  - time zone of geoposition of building
    :param date:
    :param month:
    :param year:
    :param period:
    :return: tuple (start , end) - begin and end of period.
    """
    if year and not month and not date:
        year = datetime.datetime(day=1, month=1, year=year)
        start = pd.Timestamp(year, tz=tz)
        end = start + pd.Timedelta(days=365)
    elif month and not date:
        if not year:
            year = datetime.datetime.now().year
        month = datetime.datetime(day=1, month=month, year=year)
        start = pd.Timestamp(month, tz=tz)
        end = start + pd.Timedelta(days=31)
    elif date:
        if not year:
            year = datetime.datetime.now().year
        if not month:
            month = datetime.datetime.now().month
        date = datetime.datetime(day=date, month=month, year=year)
        start = pd.Timestamp(date, tz=tz)
        end = start + pd.Timedelta(days=1)
    elif period:
        start = pd.Timestamp(period[0], tz=tz)
        end = pd.Timestamp(period[1], tz=tz)
    else:
        date = datetime.datetime.now()
        start = pd.Timestamp(date, tz=tz)
        end = start + pd.Timedelta(days=1)
    return start, end

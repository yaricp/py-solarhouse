import datetime
import pytz
import pandas as pd

from solarhouse.helpers import prepare_period

tz = pytz.timezone("Asia/Novosibirsk")


def test_year():
    start, end = prepare_period(tz=tz, year=2019)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2019-01-01 00:00:00+0700", tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2020-01-01 00:00:00+0700", tz="Asia/Novosibirsk")


def test_month():
    start, end = prepare_period(tz=tz, month=7)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2020-07-01 00:00:00+0700", tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2020-08-01 00:00:00+0700", tz="Asia/Novosibirsk")
    start, end = prepare_period(tz=tz, month=7, year=2017)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2017-07-01 00:00:00+0700", tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2017-08-01 00:00:00+0700", tz="Asia/Novosibirsk")


def test_date():
    start, end = prepare_period(tz=tz, date=17)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    month_now = datetime.datetime.now().month
    assert start == pd.Timestamp("2020-%s-17 00:00:00+0700" % month_now, tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2020-%s-18 00:00:00+0700" % month_now, tz="Asia/Novosibirsk")
    start, end = prepare_period(tz=tz, date=17, month=5)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2020-05-17 00:00:00+0700", tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2020-05-18 00:00:00+0700", tz="Asia/Novosibirsk")
    start, end = prepare_period(tz=tz, date=17, year=2017)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2017-%s-17 00:00:00+0700" % month_now, tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2017-%s-18 00:00:00+0700" % month_now, tz="Asia/Novosibirsk")
    start, end = prepare_period(tz=tz, date=17, month=5, year=2017)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2017-05-17 00:00:00+0700", tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2017-05-18 00:00:00+0700", tz="Asia/Novosibirsk")


def test_period():
    period = (
        datetime.datetime(day=12, month=6, year=2017),
        datetime.datetime(day=6, month=12, year=2017),
    )
    start, end = prepare_period(tz=tz, period=period)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp("2017-06-12 00:00:00+0700", tz="Asia/Novosibirsk")
    assert end == pd.Timestamp("2017-12-06 00:00:00+0700", tz="Asia/Novosibirsk")


def test_empty_date():
    start, end = prepare_period(tz=tz)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start.date() == pd.Timestamp(datetime.datetime.now(), tz="Asia/Novosibirsk")
    assert end.date() == pd.Timestamp(datetime.datetime.now() + datetime.timedelta(days=1), tz="Asia/Novosibirsk")

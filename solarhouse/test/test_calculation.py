import datetime
import pandas as pd

from calculation import Calculation
from test_building import create_file_mesh, remove_file_mesh


def create_calc():
    create_file_mesh()
    c = Calculation(
        tz='Asia/Novosibirsk',
        path_file_object='solarhouse/test/test_file.obj',
        geo={
            'latitude': 54.841426,
            'longitude': 83.264479},
        wall_material='cob',
        wall_thickness=0.1,
        start_temp_in=15.0,
        power_heat_inside=500,
        efficiency_collector=0.6,
    )
    remove_file_mesh()
    return c


def test_year():
    c = create_calc()
    start, end = c.prepare_period(year=2019)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2019-01-01 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2020-01-01 00:00:00+0700', tz='Asia/Novosibirsk')


def test_month():
    c = create_calc()
    start, end = c.prepare_period(month=7)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2020-07-01 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2020-08-01 00:00:00+0700', tz='Asia/Novosibirsk')
    start, end = c.prepare_period(month=7,year=2017)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2017-07-01 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2017-08-01 00:00:00+0700', tz='Asia/Novosibirsk')


def test_date():
    c = create_calc()
    start, end = c.prepare_period(date=17)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2020-04-17 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2020-04-18 00:00:00+0700', tz='Asia/Novosibirsk')
    start, end = c.prepare_period(date=17, month=5)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2020-05-17 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2020-05-18 00:00:00+0700', tz='Asia/Novosibirsk')
    start, end = c.prepare_period(date=17, year=2017)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2017-04-17 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2017-04-18 00:00:00+0700', tz='Asia/Novosibirsk')
    start, end = c.prepare_period(date=17, month=5, year=2017)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2017-05-17 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2017-05-18 00:00:00+0700', tz='Asia/Novosibirsk')


def test_period():
    c = create_calc()
    period = (datetime.datetime(day=12, month=6, year=2017), datetime.datetime(day=6, month=12, year=2017))
    start, end = c.prepare_period(period=period)
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start == pd.Timestamp('2017-06-12 00:00:00+0700', tz='Asia/Novosibirsk')
    assert end == pd.Timestamp('2017-12-06 00:00:00+0700', tz='Asia/Novosibirsk')


def test_empty_date():
    c = create_calc()
    start, end = c.prepare_period()
    assert type(start) == pd.Timestamp
    assert type(end) == pd.Timestamp
    assert start.date() == pd.Timestamp(datetime.datetime.now(), tz='Asia/Novosibirsk')
    assert end.date() == pd.Timestamp(datetime.datetime.now() + datetime.timedelta(days=1), tz='Asia/Novosibirsk')
from datetime import datetime, timedelta
from codalib.xsdatetime import (
    xsDateTime_parse, xsDateTime_format, XSDateTimezone,
    current_offset
)


# get the current utc offset for local time.
# we have to do this so tests will work during
# dst and std time
LOCAL_OFFSET = current_offset()


def test_parse_date():
    dt_str = "2017-01-27T14:43:00+00:00"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 14, 43) + LOCAL_OFFSET
    assert isinstance(dt, datetime)
    assert dt == equiv


def test_parse_naive():
    dt_str = "2017-02-01T15:49:33.333333"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 2, 1, 15, 49, 33, 333333)
    assert dt == equiv
    assert xsDateTime_format(dt) == dt_str


def test_parse_datetime_with_nonzero_offset():
    dt_str = "2017-01-27T15:14:00+06:00"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 9, 14) + LOCAL_OFFSET
    assert dt == equiv


def test_parse_with_nonzero_offset_microsecond():
    dt_str = "2017-01-27T15:14:00.111111+06:00"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 9, 14, 0, 111111) + LOCAL_OFFSET
    assert dt == equiv


def test_parse_with_nondefault_timezone():
    dt_str = "2017-01-27T15:14:00.111111+06:00"
    dt = xsDateTime_parse(dt_str, local_tz="US/Pacific")
    equiv = datetime(2017, 1, 27, 9, 14, 0, 111111)
    equiv += current_offset("US/Pacific")
    assert dt == equiv


def test_format_notzinfo():
    dt = datetime(2017, 1, 27, 15, 16)
    dt_str = "2017-01-27T15:16:00"
    assert xsDateTime_format(dt) == dt_str


def test_format_wtzinfo():
    dt = datetime(2017, 1, 27, 15, 16, tzinfo=XSDateTimezone(hours=6))
    dt_str = "2017-01-27T15:16:00+06:00"
    assert xsDateTime_format(dt) == dt_str


def test_parse_fractional_seconds_zulu():
    dt_str = "2017-01-27T15:16:00.59Z"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 15, 16, 0, 590000)
    equiv += LOCAL_OFFSET
    assert dt == equiv


def test_parse_fractional_seconds_offset():
    dt_str = "2017-01-27T15:16:00.59-06:00"
    dt = xsDateTime_parse(dt_str)
    td = timedelta(hours=-6)
    equiv = datetime(2017, 1, 27, 21, 16, 0, 590000)
    equiv += td
    assert dt == equiv


def test_format_inandout():
    dt = datetime(2017, 1, 27, 15, 16)
    dt_str = "2017-01-27T15:16:00"
    assert xsDateTime_format(dt) == dt_str
    assert xsDateTime_parse(dt_str) == dt


def test_format_inandout_wtzinfo():
    dt = datetime(
        2017, 1, 27, 15, 16, 12, 123456, tzinfo=XSDateTimezone(hours=-11)
    )
    naive_dt = dt.replace(tzinfo=None)
    td = timedelta(hours=-11)
    # set naive datetime to utc by inverting offset
    naive_dt -= td
    # add local offset for naive local time
    naive_dt += LOCAL_OFFSET
    dt_str = "2017-01-27T15:16:12.123456-11:00"
    assert xsDateTime_format(dt) == dt_str
    assert xsDateTime_parse(dt_str) == naive_dt


def test_negative_offset():
    dt_str = "2017-01-30T12:02:00-06:00"
    dt = xsDateTime_parse(dt_str)
    td = timedelta(hours=-6)
    equiv = datetime(2017, 1, 30, 18, 2)
    equiv += td
    assert dt == equiv

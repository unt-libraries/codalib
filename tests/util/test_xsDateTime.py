from datetime import datetime, timedelta
from codalib.xsdatetime import (
    xsDateTime_parse, xsDateTime_format, XSDateTimezone,
    current_offset, localize_datetime, set_default_local_tz
)
from pytz import timezone


# Get the current utc offset for local time.
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
    dt = xsDateTime_parse(dt_str, local_tz=timezone("US/Pacific"))
    equiv = datetime(2017, 1, 27, 9, 14, 0, 111111)
    equiv += current_offset(timezone("US/Pacific"))
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
    dt = xsDateTime_parse(dt_str, local_tz=timezone("US/Central"))
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
    # Set naive datetime to utc by inverting offset
    naive_dt -= td
    # Add local offset for naive local time
    naive_dt += LOCAL_OFFSET
    dt_str = "2017-01-27T15:16:12.123456-11:00"
    assert xsDateTime_format(dt) == dt_str
    assert xsDateTime_parse(dt_str) == naive_dt


def test_negative_offset():
    dt_str = "2017-01-30T12:02:00-06:00"
    dt = xsDateTime_parse(dt_str, local_tz=timezone("US/Central"))
    td = timedelta(hours=-6)
    equiv = datetime(2017, 1, 30, 18, 2)
    equiv += td
    assert dt == equiv


def test_localize_and_format():
    dt_str = "2017-02-02T12:33:00"
    # We can't use the total_seconds method, as it's absent in 2.6
    offset_hrs = int(LOCAL_OFFSET.seconds + LOCAL_OFFSET.days*24*3600)
    offset_hrs /= (60*60)
    sign = '-' if offset_hrs < 0 else '+'
    localized_str = "2017-02-02T12:33:00{0:s}{1:02d}:00"
    localized_str = localized_str.format(sign, abs(offset_hrs))
    # XsDateTime_parse returns a naive local time
    dt = xsDateTime_parse(dt_str)
    # Localize that naive datetime so it becomes tz aware,
    # using default local timezone
    dt = localize_datetime(dt)
    # The tz-aware local time ought to format to the
    # xsdatetime string constructed above, includes offset
    assert xsDateTime_format(dt) == localized_str


def test_change_default_local_tz():
    old_local_tz = set_default_local_tz(timezone("US/Pacific"))
    dt_str = "2017-02-02T12:56:44"
    dt0 = localize_datetime(xsDateTime_parse(dt_str))
    os0 = current_offset()
    old_local_tz = set_default_local_tz(timezone("US/Central"))
    dt1 = localize_datetime(xsDateTime_parse(dt_str))
    os1 = current_offset()
    # Calculate difference in offsets between central & pacific
    # we can't use the total_seconds method, as it's absent in 2.6
    # osdiff = os0.total_seconds()-os1.total_seconds()
    osdiff = (os0.seconds + os0.days*24*3600)
    osdiff -= (os1.seconds + os1.days*24*3600)
    osdiff /= 60*60
    osdiff = int(osdiff)
    # Should have been returned as pacific
    assert old_local_tz == timezone("US/Pacific")
    # The datetimes should have been localized to different timezones
    assert dt0 != dt1
    # The difference between the offsets should be -2 hours, since
    # pacific time is 2 hours behind central
    assert osdiff == -2

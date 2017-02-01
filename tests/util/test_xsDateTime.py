from datetime import datetime
from codalib.xsdatetime import xsDateTime_parse, xsDateTime_format, XSDateTimezone


def test_parse_date():
    dt_str = "2017-01-27T14:43:00+00:00"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 8, 43)
    assert isinstance(dt, datetime)
    assert dt == equiv


def test_parse_datetime_with_nonzero_offset():
    dt_str = "2017-01-27T15:14:00+06:00"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 3, 14)
    assert dt == equiv


def test_format_notzinfo():
    dt = datetime(2017, 1, 27, 15, 16)
    dt_str = "2017-01-27T15:16:00-06:00"
    assert xsDateTime_format(dt) == dt_str


def test_format_wtzinfo():
    dt = datetime(2017, 1, 27, 15, 16, tzinfo=XSDateTimezone(hours=6))
    dt_str = "2017-01-27T15:16:00+06:00"
    assert xsDateTime_format(dt) == dt_str


def test_parse_fractional_seconds_zulu():
    dt_str = "2017-01-27T15:16:00.59Z"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 9, 16, 00, 590000)
    assert dt == equiv


def test_parse_fractional_seconds_offset():
    dt_str = "2017-01-27T15:16:00.59-06:00"
    dt = xsDateTime_parse(dt_str)
    equiv = datetime(2017, 1, 27, 15, 16, 00, 590000)
    assert dt == equiv


def test_format_inandout():
    dt = datetime(2017, 1, 27, 15, 16)
    dt_str = "2017-01-27T15:16:00-06:00"
    assert xsDateTime_format(dt) == dt_str
    assert xsDateTime_parse(dt_str) == dt


def test_negative_offset():
    dt_str = "2017-01-30T12:02:00-06:00"
    dt = xsDateTime_parse(dt_str)
    assert dt == datetime(2017, 01, 30, 12, 2, 0)

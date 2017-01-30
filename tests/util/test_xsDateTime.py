
from datetime import datetime, timedelta
from codalib.util import xsDateTime_parse, xsDateTime_format, XSDateTimezone


def test_parse_date():

    dt_str = "2017-01-27T14:43:00+00:00"
    dt = xsDateTime_parse(dt_str)
    
    assert isinstance(dt, datetime)
    assert dt.utcoffset() == timedelta(0)

def test_parse_datetime_with_nonzero_offset():

    dt_str = "2017-01-27T15:14:00+06:00"

    dt = xsDateTime_parse(dt_str)
    assert dt.utcoffset() == timedelta(hours=6)

def test_format_notzinfo():

    dt = datetime(2017, 1, 27, 15, 16)
    dt_str = "2017-01-27T15:16:00"

    assert xsDateTime_format(dt) == dt_str

def test_format_wtzinfo():

    dt = datetime(2017, 1, 27, 15, 16, tzinfo=XSDateTimezone(hours=6))
    dt_str = "2017-01-27T15:16:00+06:00"

    assert xsDateTime_format(dt) == dt_str

def test_format_inandout():

    dt = datetime(2017, 1, 27, 15, 16, tzinfo=XSDateTimezone(hours=6))
    dt_str = "2017-01-27T15:16:00+06:00"

    assert xsDateTime_format(dt) == dt_str
    assert xsDateTime_parse(dt_str) == dt

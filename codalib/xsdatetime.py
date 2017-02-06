from datetime import datetime, tzinfo, timedelta

from pytz import utc as utc_tz
from tzlocal import get_localzone

# Constants for time parsing/formatting
# This is a stub
XSDT_FMT = "%Y-%m-%dT%H:%M:%S"
# This should never change
XSDT_TZ_OFFSET = 19
# The str value to use for default local timezone
# In localization operations
DEFAULT_LOCAL_TZ = get_localzone()


class InvalidXSDateTime(Exception):
    pass


class XSDateTimezone(tzinfo):
    """
    Concrete subclass of tzinfo for making sense of timezone offsets.
    Not really worried about localization here, just +/-HHMM
    """

    def __init__(self, hours=0, minutes=0, sign=1):
        self.minutes = hours * 60 + minutes
        self.minutes *= sign

    def utcoffset(self, dt):
        return timedelta(minutes=self.minutes)

    def dst(self, dt):
        return timedelta(0)


def xsDateTime_parse(xdt_str, local_tz=None):
    """
    Parses xsDateTime strings of form 2017-01-27T14:58:00+0600, etc.
    Returns a *naive* datetime in local time according to local_tz.
    """
    if not isinstance(xdt_str, basestring):
        raise InvalidXSDateTime(
            "Expecting str or unicode, got {}.".format(type(xdt_str))
        )

    try:
        # This won't parse the offset (or other tzinfo)
        naive_dt = datetime.strptime(xdt_str[0:XSDT_TZ_OFFSET], XSDT_FMT)
    except:
        raise InvalidXSDateTime("Malformed date/time ('%s')." % (xdt_str,))

    naive_len = XSDT_TZ_OFFSET
    offset_len = len(xdt_str) - naive_len
    offset_str = xdt_str[-offset_len:]
    offset_hours = None
    offset_minutes = None
    offset_sign = 1
    parsed = None

    # Parse fractional seconds if present
    fsec_i = 0
    if not offset_len:
        parsed = naive_dt
    elif offset_str[0] is '.':
        if offset_len > 1:
            fsec_i = 1
            fsec_chr = offset_str[fsec_i]
            fsec = ''
            while fsec_chr.isdigit():
                fsec += fsec_chr
                fsec_i += 1
                if fsec_i >= offset_len:
                    break
                fsec_chr = offset_str[fsec_i]
            fsec = float('.'+fsec)
            naive_dt += timedelta(milliseconds=fsec*1000)
        else:
            raise InvalidXSDateTime('Malformed fractional seconds.')

    # Reset offset length and set offset string to actual offset,
    # if we found fractional seconds -- otherwise this is all a noop
    offset_len -= fsec_i
    if offset_len:
        offset_str = offset_str[fsec_i:fsec_i+offset_len+1]
    else:
        offset_str = ''

    # Get local timezone info using local_tz (tzinfo)
    # throws pytz.exceptions.UnknownTimezoneError
    # on bad timezone name
    if local_tz is None:
        local_tz = DEFAULT_LOCAL_TZ

    # Parse offset
    if not offset_len:
        # If there is no offset, assume local time
        # and return the naive datetime we have
        parsed = naive_dt
        return parsed
    # +00:00
    elif offset_len is 6:
        if offset_str[0] not in "+-":
            raise InvalidXSDateTime("Malformed offset (missing sign).")
        elif offset_str[0] is '-':
            offset_sign = -1
        try:
            offset_hours = int(offset_str[1:3])
        except:
            raise InvalidXSDateTime("Malformed offset (invalid hours '%s')"
                                    % (offset_str[1:3],))
        if offset_str[3] is not ':':
            raise InvalidXSDateTime("Colon missing in offset (no colon).")
        try:
            offset_minutes = int(offset_str[4:6])
        except:
            raise InvalidXSDateTime("Malformed offset (invalid minutes '%s')"
                                    % (offset_str[4:6],))
        offset = offset_hours * 60 + offset_minutes
        offset *= offset_sign
        faux_timezone = XSDateTimezone(offset_hours, offset_minutes, offset_sign)
        parsed = naive_dt.replace(tzinfo=faux_timezone)
    # Z
    elif offset_len is 1:
        if offset_str is 'Z':
            parsed = naive_dt.replace(tzinfo=XSDateTimezone())
        else:
            raise InvalidXSDateTime("Unrecognized timezone identifier '%s'." %
                                    (offset_str,))
    else:
        raise InvalidXSDateTime("Malformed offset '%s'." % (offset_str,))

    # We've parsed the offset str. now,
    # Flatten datetime w/ tzinfo into a
    # Naive datetime, utc
    offset = parsed.utcoffset()
    parsed = parsed.replace(tzinfo=None)
    if offset is not None:
        parsed -= offset
    # Add utc timezone info
    parsed = utc_tz.localize(parsed)
    # Convert to local timezone and make naive again
    parsed = parsed.astimezone(local_tz).replace(tzinfo=None)

    return parsed


def xsDateTime_format(xdt):
    """
    Takes naive or timezone aware datetime and returns a xs:datetime
    compliant string.
    """
    return xdt.isoformat()


def localize_datetime(dt, local_tz=None):
    """
    Takes a naive datetime and makes it timezone-aware,
    using the optional local_tz (tzinfo) kwarg. Useful for forcing
    xsDateTime_format to include offsets.
    """
    if local_tz is None:
        local_tz = DEFAULT_LOCAL_TZ
    return local_tz.localize(dt)


def current_offset(local_tz=None):
    """
    Returns current utcoffset for a timezone. Uses
    DEFAULT_LOCAL_TZ by default. That value can be
    changed at runtime using the func below.
    """
    if local_tz is None:
        local_tz = DEFAULT_LOCAL_TZ
    dt = local_tz.localize(datetime.now())
    return dt.utcoffset()


def set_default_local_tz(new_local_tz):
    """
    Sets the default local timezone using new_local_tz
    Returns the previous default timezone info object
    """
    global DEFAULT_LOCAL_TZ
    old_local_tz = DEFAULT_LOCAL_TZ
    DEFAULT_LOCAL_TZ = new_local_tz
    return old_local_tz

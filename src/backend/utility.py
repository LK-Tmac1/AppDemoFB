from datetime import datetime
from dateutil import tz
import time


def get_min_schedule_date(min_offset=5):
    min_schedule_date_time = int(time.time()) + min_offset * 60
    return datetime.fromtimestamp(min_schedule_date_time).strftime('%Y-%m-%dT%H:%M')


def parse_str_date(str_date):
    if not str_date:
        return ""
    try:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        str_date = str_date.split("+")
        utc = datetime.strptime(str_date[0], '%Y-%m-%dT%H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local_time = utc.astimezone(to_zone)
        date_str = '%s-%s-%s %s:%s' % (local_time.year, local_time.month, local_time.day,
                                       local_time.hour, local_time.minute)
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %I:%M %p')
    except Exception:
        return str_date


def unix_to_real_time(unix_int):
    try:
        return datetime.fromtimestamp(unix_int).strftime('%Y-%m-%d %I:%M %p')
    except Exception:
        return ""


def real_time_to_unix(date_time_str):
    date_time_str = date_time_str.replace("T", " ")
    return int(datetime.strptime(date_time_str, '%Y-%m-%d %H:%M').strftime("%s"))


#print real_time_to_unix("2017-10-21T00:00")

# print parse_str_date("2017-10-14T05:36:33+0000")

# print unix_to_real_time(1512196140)

#print get_min_schedule_date()

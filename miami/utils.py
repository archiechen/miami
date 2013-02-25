from datetime import datetime,timedelta

def now():
    return datetime.now()

def get_last_monday():
    ctime = now().replace(hour=0, minute=0, second=0, microsecond=0)
    td = timedelta(days=(ctime.weekday() + 7))
    return ctime - td

def get_last_tuesday():
    ctime = now().replace(hour=0, minute=0, second=0, microsecond=0)
    td = timedelta(days=(ctime.weekday() + 6))
    return ctime - td


def get_current_monday():
    ctime = now().replace(hour=0, minute=0, second=0, microsecond=0)
    td = timedelta(days=ctime.weekday())
    return ctime - td


def get_next_monday():
    td = timedelta(days=7)
    return get_current_monday() + td

def yestoday():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=1)

def today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time 
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return  "a minute ago"
        if second_diff < 3600:
            return str( second_diff / 60 ) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str( second_diff / 3600 ) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff/7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff/30) + " months ago"
    return str(day_diff/365) + " years ago"
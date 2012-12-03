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
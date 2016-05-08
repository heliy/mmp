#coding:UTF-8

from datetime import datetime

def format_datetime(timestamp):
    """Format a timestamp for display."""
    return datetime.utcfromtimestamp(timestamp).strftime('%Y-%m-%d @ %H:%M')

def date(infos, name):
    items = ['year', 'month', 'day', 'hour', 'min']
    for item in items:
        key = name+"_"+item
        if name+"_"+item not in infos:
            return "You need enter the %s in %s date" % (item, name)
        try:
            int(infos[key])
        except ValueError:
            return "You need enter correct %s in %s date" % (item, name)
    try:
        date = datetime(year=int(infos[name+"_year"]), month=int(infos[name+"_month"]),
                                 day=int(infos[name+"_day"]), hour=int(infos[name+"_hour"]),
                                 minute=int(infos[name+"_min"]))
    except ValueError:
        return "You need enter correct %s date" % name
    return int(date.timestamp())


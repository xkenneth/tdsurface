from django import template
register = template.Library()

import pytz


@register.filter
def utc2tz(value, tz):
    """
    Given a naive datetime in UTC, returns a naive datetime converted to timezone tz .
    """
    try:  
        tzi = pytz.timezone(tz)
        return pytz.utc.localize(value).astimezone(tzi).replace(tzinfo=None)
    except:
        return value

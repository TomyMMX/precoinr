from datetime import datetime
from django.utils.timezone import utc

from django.utils import timezone
from django.utils import formats

def now():
    return datetime.utcnow().replace(tzinfo=utc)

def get_tz_date(dt, meth, tz):
    dt = meth(dt, timezone.utc)
    return dt

def make_naive(dt, tz='utc'):
    dt = get_tz_date(dt, timezone.make_naive, tz)
    return dt

def make_aware(dt, tz='utc'):
    dt = dt.replace(tzinfo=utc)
    return dt

def local_dateformat(dt):
    return formats.localize(localtime(dt), use_l10n=False)

def localtime(dt):
    return timezone.localtime(dt)

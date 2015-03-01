from __future__ import unicode_literals

import datetime
import urlparse
import urllib

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
from django.conf import settings
settings._target = None

from google.appengine.api import memcache

from django.utils.timezone import is_aware, utc
from django.utils.translation import ugettext, ungettext_lazy

import comment_helper

def length(item):
    return len(item)

def comment_count(item):
    count = memcache.get('topcount_%d' % item.key().id())
    if not count:
        count = comment_helper.get_comment_count_for_item(item)
        memcache.set(key='topcount_%d' % item.key().id(), value=count)
    return count

def urlencode(string):
    return urllib.quote_plus(str(string))

def get_base_url(url):
    parse_object = urlparse.urlparse(url)
    return parse_object.netloc

def pluralize(value):
    if value == 1:
        return ''
    return 's'

def avoid_wrapping(value):
    return value.replace(" ", "\xa0")

def timesince(d, now=None, reversed=False):
    """
    Takes two datetime objects and returns the time between d and now
    as a nicely formatted string, e.g. "10 minutes".  If d occurs after now,
    then "0 minutes" is returned.

    Units used are years, months, weeks, days, hours, and minutes.
    Seconds and microseconds are ignored.  Up to two adjacent units will be
    displayed.  For example, "2 weeks, 3 days" and "1 year, 3 months" are
    possible outputs, but "2 weeks, 3 hours" and "1 year, 5 days" are not.

    Adapted from
    http://web.archive.org/web/20060617175230/http://blog.natbat.co.uk/archive/2003/Jun/14/time_since
    """
    chunks = (
        (60 * 60 * 24 * 365, '%d year'),
        (60 * 60 * 24 * 30, '%d month'),
        (60 * 60 * 24 * 7, '%d week'),
        (60 * 60 * 24, '%d day'),
        (60 * 60, '%d hour'),
        (60, '%d minute')
    )
    # Convert datetime.date to datetime.datetime for comparison.
    if not isinstance(d, datetime.datetime):
        d = datetime.datetime(d.year, d.month, d.day)
    if now and not isinstance(now, datetime.datetime):
        now = datetime.datetime(now.year, now.month, now.day)

    if not now:
        now = datetime.datetime.now(utc if is_aware(d) else None)
    delta = (d - now) if reversed else (now - d)
    # ignore microseconds
    since = delta.days * 24 * 60 * 60 + delta.seconds
    if since <= 0:
        # d is in the future compared to now, stop processing.
        return avoid_wrapping(ugettext('0 minutes'))
    for i, (seconds, name) in enumerate(chunks):
        count = since // seconds
        if count != 0:
            break
    result = avoid_wrapping(('%s%s' % (name, pluralize(count))) % count)
    '''if i + 1 < len(chunks):
        # Now get the second item
        seconds2, name2 = chunks[i + 1]
        count2 = (since - (seconds * count)) // seconds2
        if count2 != 0:
            result = '%s, ' % result
            result += avoid_wrapping(('%s%s' % (name2, pluralize(count2))) % count2)'''
    return result
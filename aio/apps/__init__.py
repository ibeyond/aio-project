# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import db

from datetime import datetime,timedelta
from apps.db import AIOBase, Counter
import simplejson, gdata, atom
import os, logging, re

encoding = 'utf-8'

timedelta_seconds = 28800

twitter_service = 'twitter'
twitter_user_timeline_url = 'https://twitter.com/statuses/user_timeline.json'
twitter_status_counter = 'twitter_status'
twitter_import_counter = 'twitter_import'
twitter_max_count = 10

    
def make_blog_post(title, content, term):
    entry = gdata.GDataEntry()
    entry.title = atom.Title('xhtml', title)
    entry.content = atom.Content(content_type='html', text=content)
    entry.category = [atom.Category(term=category, scheme='http://www.blogger.com/atom/ns#') for category in term if category != '']
    return entry.ToString(encoding)


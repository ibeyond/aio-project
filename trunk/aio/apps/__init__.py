# -*- coding: utf-8 -*-

from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import db
from random import getrandbits
from time import time
from hmac import new as hmac
from urllib import urlencode, quote as urlquote
from hashlib import sha1
from datetime import datetime,timedelta
from apps.db import AIOBase, Counter
import simplejson, os, logging, re, gdata, atom

encoding = 'utf-8'

timedelta_seconds = 28800

    
def make_blog_post(title, content, term):
    entry = gdata.GDataEntry()
    entry.title = atom.Title('xhtml', title)
    entry.content = atom.Content(content_type='html', text=content)
    entry.category = [atom.Category(term=category, scheme='http://www.blogger.com/atom/ns#') for category in term if category != '']
    return entry.ToString(encoding)


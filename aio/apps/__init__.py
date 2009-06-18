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


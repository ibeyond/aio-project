# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
from home.models import FeedBase
from home.models import EntryBase

class Entry(EntryBase):
    pass
    #feed = db.ReferenceProperty(FeedBase)
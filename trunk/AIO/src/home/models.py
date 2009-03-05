# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db

   
class Feed(db.Model):
    feed_title = db.StringProperty()
    feed_id = db.StringProperty()
    feed_html_link = db.LinkProperty()
    feed_description = db.StringProperty()
    feed_language = db.StringProperty()
    feed_copy_right = db.StringProperty()
    feed_author = db.ReferenceProperty(db.UserProperty)
    feed_last_update_date = db.DateTimeProperty()
    feed_category = db.StringProperty()
    feed_categary_scheme = db.StringProperty()
    feed


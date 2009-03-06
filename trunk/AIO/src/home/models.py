# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db
   
class FeedBase(db.Model):
    """Feed Base"""
    feed_title = db.StringProperty()
    feed_id = db.StringProperty()
    feed_html_link = db.LinkProperty()
    feed_description = db.StringProperty()
    feed_language = db.StringProperty()
    feed_copy_right = db.StringProperty()
    feed_author = db.UserProperty()
    feed_last_update_date = db.DateTimeProperty()
    feed_category = db.StringProperty()
    feed_categary_scheme = db.StringProperty()
    feed_generator = db.StringProperty()
    feed_icon = db.LinkProperty()
    feed_logo = db.LinkProperty()

class EntryBase(db.Model):
    """Entry Base"""
    entry_id = db.StringProperty()
    entry_title = db.StringProperty()
    entry_link = db.LinkProperty()
    entry_summary = db.TextProperty()
    entry_content = db.TextProperty()
    entry_author = db.UserProperty()
    entry_category = db.StringProperty()
    entry_category_scheme = db.StringProperty()
    entry_publication_date = db.DateTimeProperty()
    entry_update_date = db.DateTimeProperty()
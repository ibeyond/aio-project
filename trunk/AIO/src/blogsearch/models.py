# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from google.appengine.ext import db

class BlogEntry(db.Model):
    """’ŸŽq"""

    entry_title = db.StringProperty(required=True)
    date = db.DateTimeProperty(auto_now=True)
    entry_contents = db.TextProperty(required=True)
    entry_link = db.LinkProperty(required=True)
    create_time = db.DateTimeProperty()
    update_time = db.DateTimeProperty()
    
    def __unicode__(self):
        return '%s = %s' % ('blogsearch','result')

# -*- coding: utf-8 -*-

from apps.lib.aio import AIOProcessor
from apps.db import TwitterStatus, BlogSite
from google.appengine.ext import db
from apps.cron import *

class Clean(AIOProcessor):
    def clean_twitter(self):
        db.delete(TwitterStatus.all().fetch(300))
        reset_counter(self.user, twitter_status_counter)
        reset_counter(self.user, twitter_import_counter)
        pass

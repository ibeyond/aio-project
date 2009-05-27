# -*- coding: utf-8 -*-

import apps
from apps.stored import TwitterStatus
from google.appengine.ext import db
from apps.cron import *

class Clean(apps.AIOProcessor):
    def clean_twitter(self):
        db.delete(TwitterStatus.all().fetch(300))
        reset_counter(self.user, twitter_status_counter)
        reset_counter(self.user, twitter_import_counter)
        pass
        
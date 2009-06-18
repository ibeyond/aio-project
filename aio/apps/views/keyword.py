# -*- coding: utf-8 -*-

import apps
from apps.lib.aio import AIOProcessor
from apps.db import Keyword as db_Keyword
from apps.lib.aio import AIOException
from google.appengine.ext import db

class Keyword(AIOProcessor):
    def index(self):
        self.page_data['keywords'] = db_Keyword.all().filter('user =', self.user).order('-updated')
        
    def _add_keyword(self):
        error = self.check_params()
        if not error:
            keyword = db_Keyword.all().filter('user =', self.user).filter('name =', self.form['keyword_name']).get()
            if keyword is None:
                keyword = db_Keyword(user=self.user, **self.form)
            else:
                keyword.key_value = self.form['keyword_value']
                keyword.key_category = self.form['keyword_category']
            keyword.put()
        else:
            raise AIOException(error)
        self.redirect('/keyword')
    def _del_keyword(self):
        error = self.check_params()
        if not error:
            db.delete(self.form['key'])
        else:
            raise AIOException(error)
        self.redirect('/keyword')
        
          
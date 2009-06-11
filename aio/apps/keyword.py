# -*- coding: utf-8 -*-

import apps

from apps.stored import Keyword as db_Keyword

class Keyword(apps.AIOProcessor):
    def index(self):
        self.page_data['keywords'] = db_Keyword.all().filter('user =', self.user).order('-updated')
        
    def add_keyword(self):
        error = self.check_params()
        if error:
            self.log.info(error)
        else:
            keyword = db_Keyword.all().filter('user =', self.user).filter('name =', self.form['keyword_name']).get()
            if keyword is None:
                keyword = db_Keyword(user=self.user, **self.form)
            else:
                keyword.key_value = self.form['keyword_value']
                keyword.key_category = self.form['keyword_category']
            keyword.put()
        self.redirect('/keyword')  
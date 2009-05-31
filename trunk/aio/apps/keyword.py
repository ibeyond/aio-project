# -*- coding: utf-8 -*-

import apps

from apps.stored import Keyword as db_Keyword

class Keyword(apps.AIOProcessor):
    def index(self):
        self.page_data['keywords'] = db_Keyword.all().filter('user =', self.user).order('-updated')
        
    def add_keyword(self):
        key_name = self.request.get('key_name')
        key_value = self.request.get('key_value')
        if key_name != '' and key_value != '':
            keyword = db_Keyword.all().filter('user =', self.user).filter('name =', key_name).get()
            if keyword is None:
                keyword = db_Keyword(user=self.user, name=key_name, value=key_value)
            else:
                keyword.value = key_value
            keyword.put()
#        self.result['body'] = ''
        self.redirect('/keyword')  
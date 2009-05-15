# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db
import os

import apps
from appengine_utilities import sessions

'''

Created on 2009/05/14

@author: iBeyond
'''
class MainPage(webapp.RequestHandler):
    '''
    '''
    def get(self):
        self.session = sessions.Session()
        self.user = users.get_current_user()
        
        self.session['user'] = 'ibeyond'        
        if self.user:
            if not LocalAccount.all().filter('user =', self.user).get():
                LocalAccount(user=self.user).put()
    
        self.page_data = apps.make_user_data(self)
        write = self.response.out.write
        path = apps.get_template_path(__file__, 'index.html')
        write(template.render(path, self.page_data))


class LocalAccount(db.Model):
    user = db.UserProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

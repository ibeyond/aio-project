# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db
import os

from apps import *
'''
欢迎�?

Created on 2009/05/14

@author: iBeyond
'''
class MainPage(webapp.RequestHandler):
    '''
        显示欢迎�?
    '''
    def get(self):
        self.page_data = make_user_data()
        self.user = users.get_current_user()
        if self.user:
            if not LocalAccount.all().filter('user =', self.user).get():
                LocalAccount(user=self.user).put()
        write = self.response.out.write
        path = get_template_path(__file__, 'index.html')
        write(template.render(path, self.page_data))


class LocalAccount(db.Model):
    user = db.UserProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

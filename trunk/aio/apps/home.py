# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext import db
import os

from apps import *
'''
欢迎页

Created on 2009/05/14

@author: iBeyond
'''
class MainPage(webapp.RequestHandler):
    '''
        显示欢迎页
    '''
    def get(self):
        self.page_data = make_user_data()
        self.user = users.get_current_user()
        if self.user:
            if not LocalAccount.all().filter('user =', user).get():
                local_account = LocalAccount(user=user)
                local_account.put()
        write = self.response.out.write
        path = get_template_path(__file__, 'index.html')
        write(template.render(path, self.page_data))


class LocalAccount(db.Model):
    user = db.UserProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)

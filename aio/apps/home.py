# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import os, logging
import apps
class Home(webapp.RequestHandler):
    '''
    欢迎页
    '''
    def get(self):
        from apps.stored import TwitterStatus
        from google.appengine.ext import db
        db.delete(TwitterStatus.all().fetch(400))
        page_data = {}
        user = users.get_current_user()
        if user:
            apps.reg_account(user)
            page_data['user'] = user
        write = self.response.out.write
        path = os.path.join(os.path.dirname(__file__), 
                            'templates/%s/%s.html' % (self.__class__.__name__.lower(), 'index'))
        
        page_data['login_url'] = users.create_login_url('/')
        write(template.render(path, page_data))
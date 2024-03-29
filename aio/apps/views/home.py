# -*- coding: utf-8 -*-

from google.appengine.api import users, memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import os, logging
from apps.lib.user import reg_account

from apps.db import TwitterStatus, BlogPost
class Home(webapp.RequestHandler):
    def get(self):
        memcache.flush_all()
        page_data = {}
        user = users.get_current_user()
        if user:
#            reg_account(user)
            page_data['user'] = user
        write = self.response.out.write
        path = os.path.join(os.path.dirname(__file__), 
                            'templates/%s/%s.html' % (self.__class__.__name__.lower(), 'index'))
        page_data['login_url'] = users.create_login_url('/')
        page_data['logut_url'] = users.create_logout_url('/')
        page_data['twitter_status'] = TwitterStatus.all().order('-published_at').fetch(20)
#        page_data['blog_post'] = BlogPost.all().order('-updated_at').fetch(20)
        write(template.render(path, page_data))

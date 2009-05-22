# -*- coding: utf-8 -*-

'''
Created on 2009/05/18

@author: iBeyond
'''

from google.appengine.ext import webapp
from google.appengine.api import users
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required
import logging
import apps
from apps import GReaderSharedPost

class GoogleReader(webapp.RequestHandler):
    greader_prefix = 'https://www.google.com/reader/public/atom/user%2F'
    greader_suffix = '%2Fstate%2Fcom.google%2Fbroadcast'
    service = 'greader'
    @login_required
    def get(self,action=None):
        logging.info('### %s ###' % self.request.uri)
        self.user = users.get_current_user();
        self.write = self.response.out.write
        self.page_data = apps.make_user_data(self)
        if action is not None:
            getattr(self,action,self.show)()
        else:
            self.show()
        path = apps.get_template_path(__file__, 'index.html')
        self.write(template.render(path, self.page_data, debug=True))
        
    def show(self):
        import datetime
        today = datetime.datetime.today();
        curr_date = datetime.datetime(today.year,today.month,today.day)
        self.page_data['local_now'] = curr_date
        date_param = self.request.get('date') 
        if  date_param != '':
            curr_date = datetime.datetime(int(date_param.split('-')[0]),int(date_param.split('-')[1]),int(date_param.split('-')[2]))
        self.page_data['time_links'] = [curr_date - datetime.timedelta(days=i) for i in range(1,8)]
        curr_date -= datetime.timedelta(seconds=apps.timedelta_seconds)
        self.page_data['shared_posts'] = GReaderSharedPost.all().filter('user =', self.user).filter('published_at <', (curr_date + datetime.timedelta(days=1))).filter('published_at >=', curr_date).order('-published_at')        

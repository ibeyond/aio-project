# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from datetime import datetime
import simplejson
import logging
import apps

from apps.twitter import Twitter, TwitterUser, TwitterStatus, OAuthAccessToken
'''
Created on 2009/05/14

@author: iBeyond
'''

class Cron(webapp.RequestHandler):
    '''
    classdocs
    '''


    def get(self, action):
        logging.info('%s task start: [%s]' % (action ,datetime.now()))
        getattr(self, action,'index')()
        logging.info('%s task end: [%s]' % (action ,datetime.now()))
        pass
    
    def index(self):
        self.redirect('/')
    
    def twitter(self):
        for twitter_user in TwitterUser.all():
            access_token = OAuthAccessToken.all().filter('user =', twitter_user.user).get()
            if access_token is not None:
                page_no = 1
                if self.request.get('page') != '': page_no = int(self.request.get('page'))
                status = simplejson.loads(apps.get_data_from_signed_url(Twitter.user_timeline_url, access_token, **{'page':page_no, 'count':10}), apps.encoding)
                page_no += 1
                for s in status:
                    s = dict((str(k), v) for k, v in s.items())
                    s['status_id'] = s['id']
                    s['twitter_user_id'] = s['user']['id']
                    del s['user']
                    twitter_entry = TwitterStatus.all().filter('status_id =', s['id']).get()
                    if twitter_entry is None:
                        TwitterStatus(user=twitter_user.user, twitter_user=twitter_user, **s).put()
                if page_no > 10:pass
                else:
                    self.redirect('/corn/twitter?page=%s' % page_no)
        pass
        

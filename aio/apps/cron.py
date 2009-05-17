# -*- coding: utf-8 -*-

from google.appengine.ext import webapp, db
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

    twitter_max_count = 10
    twitter_import_counter = 'twitter_import_counter'
    
    def get(self, action):
        getattr(self, action,self.index)()
        pass
    
    def index(self):
        self.redirect('/')
    
    def twitter_import(self):
        for twitter_user in TwitterUser.all():
            access_token = OAuthAccessToken.all().filter('user =', twitter_user.user).get()
            if access_token is not None:
                user_info = simplejson.loads(apps.get_data_from_signed_url(Twitter.user_show_url, access_token, **{'user_id':access_token.user_id}))
                user_info = dict((str(k), v) for k, v in user_info.items())
                user_info['user_id'] = user_info['id']
                del user_info['id']
                twitter_user = TwitterUser.all().filter('user_id =', user_info['user_id']).get()
                if twitter_user is not None: 
                    for k, v in user_info.items():
                        twitter_user.__setattr__(k , v)
                twitter_user.put()
                status = simplejson.loads(apps.get_data_from_signed_url(Twitter.user_timeline_url, access_token, **{'count':Cron.twitter_max_count}), apps.encoding)
                apps.add_status(status, access_token.user, twitter_user)
                if (apps.get_count(twitter_user.user, Twitter.twitter_status_counter) < twitter_user.statuses_count):
                    if ((apps.get_count(twitter_user.user, Cron.twitter_import_counter, init_value=2)-1) * Cron.twitter_max_count) > twitter_user.statuses_count:
                        if apps.get_count(twitter_user.user, Cron.twitter_import_counter) > 2:
                            apps.reset_counter(twitter_user.user, Cron.twitter_import_counter)
                    page_no = apps.get_count(user=twitter_user.user, name=Cron.twitter_import_counter, init_value=2)
                    status = simplejson.loads(apps.get_data_from_signed_url(Twitter.user_timeline_url, access_token, **{'page':page_no, 'count':Cron.twitter_max_count}), apps.encoding)
                    apps.add_status(status, access_token.user, twitter_user)
                    apps.add_count(twitter_user.user, Cron.twitter_import_counter, 1)
            else:
                apps.reset_counter(twitter_user.user, Cron.twitter_import_counter)

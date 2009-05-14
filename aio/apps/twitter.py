# -*- coding: utf-8 -*-

'''
Twitter应用页

Created on 2009/05/14

@author: iBeyond
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.webapp.util import login_required
import logging
import simplejson
from apps import *

class Twitter(webapp.RequestHandler):
    request_token_url = 'https://twitter.com/oauth/request_token'
    access_token_url = 'https://twitter.com/oauth/access_token'
    user_auth_url = 'https://twitter.com/oauth/authorize'
    user_timeline_url = 'https://twitter.com/statuses/user_timeline.json'
    user_show_url = 'https://twitter.com/users/show.json'
    max_entry_count = 20

    '''
    '''
    @login_required
    def get(self, action=None):
        self.user = users.get_current_user();
        self.page_data = make_user_data()
        write = self.response.out.write
        self.access_token = None
        
        access_token = OAuthAccessToken.all().filter('user =', self.user).order('-created')
        if access_token.count() > 0:
            self.access_token = access_token.get()
        if action is not None:
            try:
                getattr(self, action)()
            except Exception, e:
                logging.exception(e)
                raise e
            finally:
                self.redirect('/twitter')
                return
        else:
            if self.access_token is None:
                for req_token in OAuthRequestToken.all():
                    req_token.delete()
                token_info = get_request_token_info(Twitter.request_token_url)
                request_token = OAuthRequestToken(
                                                  user=self.user,
                                                  service='twitter',
                                                  **dict(token.split('=') for token in token_info.split('&'))
                                                  )
                logging.info(dict(token.split('=') for token in token_info.split('&')))
                request_token.put()
                self.redirect(get_signed_url(Twitter.user_auth_url, request_token))
                return
            else:
                self.page_data['user_info'] = TwitterUser.all().filter('user =', self.user).get()
                self.page_data['twitter_status'] = TwitterStatus.all().filter('twitter_user =', self.page_data['user_info']).order('-status_id').fetch(20)
                pass

        path = get_template_path(__file__, 'index.html')
        write(template.render(path, self.page_data, debug=True))
        
    def update(self):
        db.delete(TwitterStatus.all())
        status = simplejson.loads(get_data_from_signed_url(Twitter.user_timeline_url, self.access_token, **{'page':self.request.get('page'), 'count':Twitter.max_entry_count}), 'utf-8')
        for s in status:
            s = dict((str(k), v) for k, v in s.items())
            s['status_id'] = s['id']
            s['twitter_user_id'] = s['user']['id']
            del s['user']
            twitter_entry = TwitterStatus.all().filter('status_id =', s['id']).get()
            if twitter_entry is None:
                TwitterStatus(user=self.user, twitter_user=TwitterUser.all().filter('user_id =', s['twitter_user_id']).get(), **s).put()
                
    def import_entry(self):
        status = simplejson.loads(get_data_from_signed_url(Twitter.user_timeline_url, self.access_token, **{'page':self.request.get('page'), 'count':Twitter.max_entry_count}), 'utf-8')
        logging.info('==================== import start =================')
        for s in status:
            logging.info(['%s = %s' % (k, v) for k, v in s.items()])
        logging.info('==================== import stop =================')
        self.page_data['status'] = status;
        pass
        
    def import_user(self):
        user_info = simplejson.loads(get_data_from_signed_url(Twitter.user_show_url, self.access_token, **{'user_id':self.access_token.user_id}))
        user_info = dict((str(k), v) for k, v in user_info.items())
        user_info['user_id'] = user_info['id']
        twitter_user = TwitterUser.all().filter('user_id =', user_info['user_id']).get()
        if twitter_user is not None: 
            for k,v in user_info.items():
                twitter_user.__setattr__(k ,v)
        else:
            twitter_user = TwitterUser(user=self.user, **user_info)
        twitter_user.put()
        
        
    def token(self):
        request_token = OAuthRequestToken.all().filter('user =', self.user).filter('service =', 'twitter').filter('oauth_token =', self.request.get('oauth_token')).get()
        token_info = get_data_from_signed_url(Twitter.access_token_url, request_token)
        access_token = OAuthAccessToken(
                                        user=self.user,
                                        service='twitter',
                                        **dict(token.split('=') for token in token_info.split('&'))
                                        )
        access_token.put()
        request_token.delete()
        
    def timeline(self):
        logging.info(get_data_from_signed_url(Twitter.rate_limit_url, self.access_token))
        

class TwitterUser(db.Model):
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    user_id = db.IntegerProperty()
    name = db.StringProperty()
    screen_name = db.StringProperty()
    location = db.StringProperty()
    description = db.StringProperty()
    profile_image_url = db.StringProperty()
    url = db.StringProperty()
    protected = db.BooleanProperty()
    followers_count = db.IntegerProperty()
    friends_count = db.IntegerProperty()
    created_at = db.StringProperty()
    favourites_count = db.IntegerProperty()
    utc_offset = db.IntegerProperty()
    time_zone = db.StringProperty()
    statuses_count = db.IntegerProperty()
    notifications = db.BooleanProperty()
    following = db.BooleanProperty()

class TwitterStatus(db.Model):
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    status_id = db.IntegerProperty()
    text = db.StringProperty()
    source = db.StringProperty()
    truncated = db.BooleanProperty()
    in_reply_to_status_id = db.IntegerProperty()
    in_reply_to_user_id = db.IntegerProperty()
    favorited = db.BooleanProperty()
    in_reply_to_screen_name = db.StringProperty()
    twitter_user = db.ReferenceProperty(TwitterUser)
    twitter_user_id = db.IntegerProperty()
    
        
class OAuthRequestToken(db.Model):
    """OAuth Request Token."""
    user = db.UserProperty(required=True)
    service = db.StringProperty(required=True)
    oauth_token = db.StringProperty(required=True)
    oauth_token_secret = db.StringProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
 
class OAuthAccessToken(db.Model):
    """OAuth Access Token."""
    user = db.UserProperty(required=True)
    service = db.StringProperty(required=True)
    oauth_token = db.StringProperty(required=True)
    oauth_token_secret = db.StringProperty(required=True)
    user_id = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

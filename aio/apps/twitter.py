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
    max_entry_count = 2

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
        logging.info(action);
        if action:
            try:
                getattr(self, action)()
            except Exception, e:
                logging.exception(e)
                self.redirect('/twitter')
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
                request_token.put()
                self.redirect(get_signed_url(Twitter.user_auth_url, request_token))

        path = get_template_path(__file__, 'index.html')
        write(template.render(path, self.page_data, debug=True))
    
    @login_required
    def post(self, action=None):
        getattr(self, action)()
        
    def import_user(self):
        user_info = simplejson.loads(get_data_from_signed_url(Twitter.user_show_url, self.access_token, **{'user_id':self.access_token.user_id}),'utf-8')
        logging.info('\n' + '\n'.join(['%s[%s] = %s' % (k,type(v),v,) for k,v in user_info.items()]))
        twitter_user = TwitterUser(user=self.user, **user_info)
        twitter_user.put()
        self.page_data['user_info'] = twitter_user
        pass
        
    
    def import_entry(self):
        status = simplejson.loads(get_data_from_signed_url(Twitter.user_timeline_url, self.access_token,**{'page':self.request.get('page'),'count':Twitter.max_entry_count}),'utf-8')
        logging.info('==================== import start =================')
        for s in status:
            logging.info(['%s = %s' % (k,v) for k,v in s.items()])
        logging.info('==================== import stop =================')
        self.page_data['status'] = status;
        pass
        
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
    """
    <?xml version="1.0" encoding="UTF-8"?>
    <user>
    <id>1401881</id>
    <name>Doug Williams</name>
    <screen_name>dougw</screen_name>
    <location>San Francisco, CA</location>
    <description>Twitter API Support. Internet, greed, users, dougw and opportunities are my passions.</description>
    <profile_image_url>http://s3.amazonaws.com/twitter_production/profile_images/59648642/avatar_normal.png</profile_image_url>
    <url>http://www.igudo.com</url>
    <protected>false</protected>
    <followers_count>1031</followers_count>
    <profile_background_color>9ae4e8</profile_background_color>
    <profile_text_color>000000</profile_text_color>
    <profile_link_color>0000ff</profile_link_color>
    <profile_sidebar_fill_color>e0ff92</profile_sidebar_fill_color>
    <profile_sidebar_border_color>87bc44</profile_sidebar_border_color>
    <friends_count>293</friends_count>
    <created_at>Sun Mar 18 06:42:26 +0000 2007</created_at>
    <favourites_count>0</favourites_count>
    <utc_offset>-18000</utc_offset>
    <time_zone>Eastern Time (US & Canada)</time_zone>
    <profile_background_image_url>http://s3.amazonaws.com/twitter_production/profile_background_images/2752608/twitter_bg_grass.jpg</profile_background_image_url>
    <profile_background_tile>false</profile_background_tile>
    <statuses_count>3390</statuses_count>
    <notifications>false</notifications>
    <following>false</following>
    <status>
    <created_at>Tue Apr 07 22:52:51 +0000 2009</created_at>
    <id>1472669360</id>
    <text>At least I can get your humor through tweets. RT @abdur: I don't mean this in a bad way, but genetically speaking your a cul-de-sac.</text>
    <source><a href="http://www.tweetdeck.com/">TweetDeck</a></source>
    <truncated>false</truncated>
    <in_reply_to_status_id></in_reply_to_status_id>
    <in_reply_to_user_id></in_reply_to_user_id>
    <favorited>false</favorited>
    <in_reply_to_screen_name></in_reply_to_screen_name>
    </status>
    </user>
    """
    user = db.UserProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
#    user_id = db.StringProperty()
#    name = db.StringProperty()
#    screen_name = db.StringProperty()
#    location = db.StringProperty()
#    description = db.StringProperty()
#    profile_image_url = db.StringProperty()
#    url = db.StringProperty()
#    protected = db.StringProperty()
#    followers_count = db.StringProperty()
#    friends_count = db.StringProperty()
#    created_at = db.StringProperty()
#    favourites_count = db.StringProperty()
#    utc_offset = db.StringProperty()
#    time_zone = db.StringProperty()
#    statuses_count = db.StringProperty()
#    notifications = db.StringProperty()
#    following = db.StringProperty()

class TwitterStatus(db.Model):
    """
    <status>
        <created_at>Tue Apr 07 22:52:51 +0000 2009</created_at>
        <id>1472669360</id>
        <text>At least I can get your humor through tweets. RT @abdur: I don't mean this in a bad way, but genetically speaking your a cul-de-sac.</text>
        <source>&lt;a href="http://www.tweetdeck.com/">TweetDeck&lt;/a></source>
        <truncated>false</truncated>
        <in_reply_to_status_id></in_reply_to_status_id>
        <in_reply_to_user_id></in_reply_to_user_id>
        <favorited>false</favorited>
        <in_reply_to_screen_name></in_reply_to_screen_name>
        <user>
        <id>1401881</id>
         <name>Doug Williams</name>
         <screen_name>dougw</screen_name>
         <location>San Francisco, CA</location>
         <description>Twitter API Support. Internet, greed, users, dougw and opportunities are my passions.</description>
         <profile_image_url>http://s3.amazonaws.com/twitter_production/profile_images/59648642/avatar_normal.png</profile_image_url>
         <url>http://www.igudo.com</url>
         <protected>false</protected>
         <followers_count>1027</followers_count>
         <profile_background_color>9ae4e8</profile_background_color>
         <profile_text_color>000000</profile_text_color>
         <profile_link_color>0000ff</profile_link_color>
         <profile_sidebar_fill_color>e0ff92</profile_sidebar_fill_color>
         <profile_sidebar_border_color>87bc44</profile_sidebar_border_color>
         <friends_count>293</friends_count>
         <created_at>Sun Mar 18 06:42:26 +0000 2007</created_at>
         <favourites_count>0</favourites_count>
         <utc_offset>-18000</utc_offset>
         <time_zone>Eastern Time (US & Canada)</time_zone>
         <profile_background_image_url>http://s3.amazonaws.com/twitter_production/profile_background_images/2752608/twitter_bg_grass.jpg</profile_background_image_url>
         <profile_background_tile>false</profile_background_tile>
         <statuses_count>3390</statuses_count>
         <notifications>false</notifications>
         <following>false</following>
        </user>
     </status>
    """
    user = db.UserProperty(required=True)
    text = db.StringProperty(required=True)
    source = db.StringProperty(required=True)
    twitter_id = db.IntegerProperty(required=True)
    
        
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

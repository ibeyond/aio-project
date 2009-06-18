# -*- coding: utf-8 -*-

from apps.lib.aio import AIOProcessor
from google.appengine.api import memcache
from apps.db import OAuthService, TwitterUser, TwitterStatus, BlogSite, TwitterBlog
import simplejson
import apps
from datetime import datetime, timedelta
from google.appengine.ext import db
from apps import lib
from apps.lib import aio, oauth
from apps.lib.aio import AIOException 
import logging

twitter_service = 'twitter'
twitter_user_timeline_url = 'https://twitter.com/statuses/user_timeline.json'
twitter_user_update_url = 'https://twitter.com/statuses/update.json'
twitter_user_friends_url = 'http://twitter.com/statuses/friends.json'
twitter_status_counter = 'twitter_status'
twitter_import_counter = 'twitter_import'
twitter_max_count = 20

def get_twitter_daily(user, date, sort='desc'):
#    data = memcache.get('twitter_%s_%s' %(user.email() ,str(date)))
    data = None
    if data is None:
        if sort == 'desc':
            order_term = '-published_at'
        else:
            order_term = 'published_at'
        data = TwitterStatus.all().filter('twitter_user_id =', get_twitter_user(user).user_id).filter('published_at <', (date + timedelta(days=1))).filter('published_at >=', date).order(order_term)
        if data is not None:
            memcache.add('twitter_%s_%s' %(user.email() ,str(date)), data)
    return data

def get_twitter_user(user):
    twitter_user = memcache.get('twitter_user_%s' % (user.email()))
    if twitter_user is None:
        twitter_user = TwitterUser.all().filter('user =', user).get()
        memcache.add('twitter_user+%s' % (user.email), twitter_user)
    return twitter_user

def add_status(status, user):
    update_twitter_user_flag = True
    for s in status:
        #取得用户信息
        user_info = s['user']
        user_info = dict((k, v) for k, v in user_info.items())
        user_info['user_id'] = user_info['id']
        del user_info['id']
        #更新用户信息
        twitter_user = memcache.get(r'twitter_%s' % user_info['user_id'])
        if update_twitter_user_flag and ((twitter_user is None) or twitter_user.statuses_count != user_info['statuses_count']):
            if twitter_user is None:
                twitter_user = TwitterUser.all().filter('user_id =',user_info['user_id']).get()
                if twitter_user is None:
                    twitter_user = TwitterUser(user=user)
            for k, v in user_info.items():
                if k == 'following' and v == 0:
                    v = False
                twitter_user.__setattr__(k , v)
            twitter_user.put()
            memcache.add(r'twitter_%s' % user_info['user_id'], twitter_user)
            update_twitter_user_flag = False
        #取得Status
        s = dict((str(k), v) for k, v in s.items())
        s['status_id'] = s['id']
        s['twitter_user_id'] = s['user']['id']
        del s['id']
        del s['user']
        s['published_at'] = datetime.strptime(s['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        twitter_status_user_id = r'%s_%s' % (twitter_status_counter, s['status_id']) 
        if memcache.get(twitter_status_user_id) is None:
            twitter_entry = TwitterStatus.all().filter('status_id =', s['status_id']).get()
            if twitter_entry is None:
                twitter_entry = TwitterStatus(user=twitter_user.user, twitter_user=twitter_user, **s)
                twitter_entry.put()
                lib.counter_incr(twitter_status_counter, user)


class Twitter(AIOProcessor):
    
    def index(self):
        twitter_user = get_twitter_user(self.user) 
        self.page_data['user_info'] = twitter_user
        today = datetime.today()
        curr_date = datetime(today.year, today.month, today.day)
        self.page_data['local_now'] = curr_date + timedelta(seconds=apps.timedelta_seconds)
        date_param = self.request.get('date') 
        if  date_param != '':
            self.page_data['date_param'] = date_param
            curr_date = datetime(int(date_param.split('-')[0]),int(date_param.split('-')[1]),int(date_param.split('-')[2]))
        self.page_data['time_links'] = [curr_date - timedelta(days=i) for i in range(1,8)]
        curr_date -= timedelta(seconds=apps.timedelta_seconds)
        self.page_data['twitter_status'] = get_twitter_daily(self.user, curr_date)
                    
    def setting(self):
        self.page_data['blog_site'] = BlogSite.all().filter('user =', self.user).order('-updated')
        twitter_blog = TwitterBlog.all().filter('user =', self.user).get()
        if twitter_blog is not None:
            self.page_data['twitter_blog'] = twitter_blog
            self.page_data['twitter_blog_title'] = BlogSite.all().filter('blog_id =', twitter_blog.blog_id).get().title   
        pass
    
    def import_status(self):
        page_no = self.request.get('page_no')
        if page_no == '':
            page_no = 1
        token = lib.get_token(twitter_service, self.user)
        status = simplejson.loads(oauth.get_data_from_signed_url(twitter_user_timeline_url, token, **{'page':page_no, 'count':twitter_max_count}), apps.encoding)
        if len(status) == 0:
            self.page_data['page_no'] = -1
            return
        add_status(status, self.user)
        self.page_data['page_no'] = int(page_no) + 1
    
    def _make_default_blog(self):
        blog_id = self.request.get('blog_id')
        category = self.request.get('category')
        if blog_id == '' or category == '':
            self.redirect('/twitter/setting')
            return
        db.delete(TwitterBlog.all().filter('user =', self.user))
        twitter_blog = TwitterBlog(user=self.user)
        twitter_blog.blog_id = blog_id
        twitter_blog.category = category
        twitter_blog.put()
        self.redirect('/twitter/setting') 
         
    def _post_to_twitter(self):
        error = self.check_params()
        if not error:
            token = lib.get_token(twitter_service, self.user)
            if token:
                status = simplejson.loads(oauth.get_data_from_signed_url(twitter_user_update_url, token, __meth='POST', **{'status':self.form['content'].encode(apps.encoding)}))
                add_status([status], self.user)
        else:
            raise AIOException(error)
        self.redirect('/twitter')
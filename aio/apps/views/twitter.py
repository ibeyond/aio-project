# -*- coding: utf-8 -*-
from apps.lib.aio import AIOProcessor
from google.appengine.api import memcache
from apps.db import OAuthService, TwitterUser, TwitterStatus, BlogSite, TwitterBlog
from apps.cron import Cron
import simplejson
import apps
from datetime import datetime, timedelta
from google.appengine.ext import db

service_name = 'twitter'

class Twitter(AIOProcessor):
    
    def index(self):
        memcache.flush_all()
        twitter_user = apps.get_twitter_user(self.user) 
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
        self.page_data['twitter_status'] = apps.get_twitter_daily(self.user, curr_date)
                    
    def setting(self):
        self.page_data['blog_site'] = BlogSite.all().filter('user =', self.user).order('-updated')
        twitter_blog = TwitterBlog.all().filter('user =', self.user).get()
        if twitter_blog is not None:
            self.page_data['twitter_blog'] = twitter_blog
            self.page_data['twitter_blog_title'] = BlogSite.all().filter('blog_id =', twitter_blog.blog_id).get().title   
        pass
    
    def make_default_blog(self):
        blog_id = self.request.get('blog_id')
        category = self.request.get('category')
        self.log.info(blog_id)
        if blog_id == '' or category == '':
            self.redirect('/twitter/setting')
            return
        db.delete(TwitterBlog.all().filter('user =', self.user))
        twitter_blog = TwitterBlog(user=self.user)
        twitter_blog.blog_id = blog_id
        twitter_blog.category = category
        twitter_blog.put()
        self.redirect('/twitter/setting') 
         
    def post_to_twitter(self):
        error = self.check_params()
        if not error:
            token = OAuthService.all().filter('user =', self.user).filter('service_name =', service_name).get()
            if token:
                self.log.info(apps.get_data_from_signed_url('https://twitter.com/statuses/update.json', token, __meth='POST', **{'status':self.form['content'].encode(apps.encoding)}))
                pass
        else:
            self.log.info(error)
        self.redirect('/twitter')
        pass


def get_twitter_daily(user, date):
    data = memcache.get('twitter_%s_%s' %(user.email() ,str(date)))
    if data is None:
        data = TwitterStatus.all().filter('twitter_user =', get_twitter_user(user)).filter('published_at <', (date + timedelta(days=1))).filter('published_at >=', date).order('-published_at')
        memcache.add('twitter_%s_%s' %(user.email() ,str(date)), data)
    return data

def get_twitter_user(user):
    twitter_user = memcache.get('twitter_user_%s' % (user.email()))
    if twitter_user is None:
        twitter_user = TwitterUser.all().filter('user =', user).get()
        if twitter_user is None:
            import apps.cron
            apps.cron.Cron().twitter_update()
            twitter_user = TwitterUser.all().filter('user =', user).get()
            memcache.add('twitter_user+%s' % (user.email), twitter_user)
    return twitter_user
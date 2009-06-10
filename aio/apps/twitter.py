# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from apps.stored import OAuthService, TwitterUser, TwitterStatus, BlogSite, TwitterBlog
from apps.cron import Cron
import simplejson
import apps
from datetime import datetime, timedelta
from google.appengine.ext import db

service_name = 'twitter'

class Twitter(apps.AIOProcessor):
    
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
         
    def post_to(self):
        content = self.request.get('content')
        if content == '':
            self.redirect('/twitter')
            return
        token = OAuthService.all().filter('user =', self.user).filter('service_name =', service_name).get()
        if token:
            apps.get_data_from_signed_url('https://twitter.com/statuses/update.json', token, __meth='POST', **{'status':content})
        self.redirect('/twitter')
        pass
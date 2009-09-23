## -*- coding: utf-8 -*-


from google.appengine.ext import webapp, db
from google.appengine.api import memcache
from google.appengine.ext.webapp import template
import simplejson
from datetime import datetime, timedelta
import logging, gdata, atom, os
from apps.db import Account, OAuthService, Counter, BlogSite, TwitterBlog, BloggerPostError
from apps.views import twitter, blogger
from apps.lib import oauth, user, feedparser
from apps import lib
import apps

class Cron(webapp.RequestHandler):
    
    def get(self, action):
        getattr(self, action, self.index)()
        pass

    def index(self):
        self.redirect('/')
        
    def twitter_update(self):
        """
        更新全部用户Twitter
        """
        for local_user in Account.all().order('-created'):
            service = lib.get_token(twitter.twitter_service, local_user.user)
            if service is not None:
                try:
                    status = simplejson.loads(oauth.get_data_from_signed_url(twitter.twitter_user_timeline_url, service, **{'count':twitter.twitter_max_count}), apps.encoding)
                    twitter.add_status(status, service.user)
                except Exception, e:
                    logging.exception(e)
                    pass
                
    def save_counter(self):
        """
        定时保持计数器
        """
        counter_list = memcache.get('aio_counter_list')
        counter_stored_list = []
        if counter_list is not None:
            for counter_name in counter_list:
                counter_value = memcache.get(counter_name)
                counter_name_list = counter_name.split('^')
                counter = Counter.all().filter('user =', user.get_user(counter_name_list[-1])).filter('name =', counter_name_list[1]).get()
                if counter is None:
                    counter = Counter(user=user.get_user(counter_name_list[-1]), name=counter_name_list[1])
                counter.value = counter_value
                counter_stored_list.append(counter)
            db.put(counter_stored_list)
               
    def update_blog_post(self):
        all_token = OAuthService.all().filter('service_name =', blogger.blogger_service)
        for token in all_token:
            blogs = BlogSite.all().filter('user =', token.user).order('-updated')
            for blog in blogs:
                result = oauth.get_data_from_signed_url(token.realm + blog.blog_id.split('-')[-1] + '/posts/default', token)
                d = feedparser.parse(result)
                blog.total_results = int(d.feed.totalresults)
                blog.put()
                for entry in d.entries:
                    blogger.add_post(entry, blog.user, blog.blog_id)
            
    def twitter_daily_post_to_blog(self):
        """
        将Twitter Daily发布到Blogger
        """
        for twitter_blog in TwitterBlog.all().order('-created'):
            blog_id = twitter_blog.blog_id.split('-')[-1]
            token = lib.get_token(blogger.blogger_service, twitter_blog.user)
            blog_url = token.realm + blog_id + '/posts/default'
            today = datetime.today()
            curr_date = datetime(today.year, today.month, today.day)
            show_date = curr_date
            curr_date -= timedelta(seconds=apps.timedelta_seconds)
            path = os.path.join(os.path.dirname(__file__), 
                            '../views/templates/%s/%s.html' % ('twitter', 'twitter_daily'))
            twitter_daily = twitter.get_twitter_daily(twitter_blog.user, curr_date, sort='asc')
            if twitter_daily is not None:
                contents = template.render(path, {'twitter_status':twitter_daily})
                entry = blogger.make_blog_post('Twitter Daily(%s)' % (show_date.strftime('%Y-%m-%d')), contents, [twitter_blog.category])
                try:
                    oauth.get_data_from_signed_url(blog_url, token, 'POST', **{'body':entry})
                except Exception, e:
                    logging.exception(e)
                    self.redirect('/cron/twitter_daily_post_to_blog')
                    pass

    def post_to_blog_by_error(self):
        for blog in BloggerPostError.all():
            twitter_blog = TwitterBlog.all().filter('blog_id =', blog.blog_id).get()
            token = lib.get_token(blogger.blogger_service, twitter_blog.user).get()
            blog_id = blog.blog_id.split('-')[-1]
            blog_url = token.realm + blog_id + '/posts/default'
            oauth.get_data_from_signed_url(blog_url, token, 'POST', **{'body':entry})
            db.delete(blog)

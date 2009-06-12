## -*- coding: utf-8 -*-

from apps.db import AIOBase, TwitterUser, OAuthService, BlogPost
from apps.db import TwitterStatus, Counter, TwitterBlog, BlogSite
from google.appengine.ext import webapp, db
from google.appengine.api import memcache
import simplejson
from datetime import datetime, timedelta

import apps, logging, gdata, atom, os

from google.appengine.ext.webapp import template

from apps.blogger import service_name as blogger_service
from feedparser import feedparser

twitter_user_timeline_url = 'https://twitter.com/statuses/user_timeline.json'
twitter_status_counter = 'twitter_status'
twitter_import_counter = 'twitter_import'
twitter_max_count = 200

class Cron(webapp.RequestHandler):
    
    def get(self, action):
        getattr(self, action, self.index)()
        pass

    def index(self):
        self.redirect('/')
        
    def twitter_update(self):
        for local_user in AIOBase.all().order('-created'):
            service = OAuthService.all().filter('user =', local_user.user).filter('service_name =', 'twitter').get()
            if service is not None:
                try:
                    status = simplejson.loads(apps.get_data_from_signed_url(twitter_user_timeline_url, service, **{'count':twitter_max_count}), apps.encoding)
                    add_status(status, service.user)
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
                 counter_value = memcache.get(counter_list)
                 logging.info('%s = %s' % (counter_name, counter_value))
                 counter_name_list = counter_name.split('^')
                 counter = Counter.all().filter('user.email =', counter_name_list[-1]).filter('name =', counter_name_list[1]).get()
                 if counter is None:
                     counter = Counter(user=apps.get_user(counter_name_list[-1]), name=counter_name_list[1])
                 counter.value = counter_value
                 counter_stored_list.append(counter)
            db.put(counter_sotred_list)
                 
    def twitter_import(self):
        for local_user in AIOBase.all().order('-created'):
            service = OAuthService.all().filter('user =', local_user.user).filter('service_name =', 'twitter').get()
            if service is not None:
                twitter_user = memcache.get('twitter_%s' % service.user_id)
                if twitter_user is None:
                    twitter_user = TwitterUser.all().filter('user_id =',service.user_id).get()
                if (apps.get_count(twitter_user.user, twitter_status_counter) < twitter_user.statuses_count):
                    if ((apps.get_count(twitter_user.user, twitter_import_counter, init_value=2) - 1) * twitter_max_count) > twitter_user.statuses_count:
                        if apps.get_count(twitter_user.user, twitter_import_counter) > 2:
                            apps.reset_counter(twitter_user.user, twitter_import_counter)
                    page_no = apps.get_count(user=twitter_user.user, name=twitter_import_counter, init_value=2)
                    status = simplejson.loads(apps.get_data_from_signed_url(twitter_user_timeline_url, service, **{'page':page_no, 'count':5}), apps.encoding)
                    add_status(status, service.user, twitter_user)
                    apps.add_count(service.user, twitter_import_counter, 1)
                else:
                    apps.reset_counter(service.user, twitter_import_counter)
    
    def update_blog_site(self):
        all_token = OAuthService.all().filter('service_name =', blogger_service)
        for token in all_token:
            result = apps.get_data_from_signed_url(token.realm + 'default/blogs', token)
            feed = atom.CreateClassFromXMLString(atom.Feed, result)
            for entry in feed.entry:
                blog = BlogSite.all().filter('blog_id =', entry.id.text).get()
                if blog is None:
                    blog = BlogSite(user=token.user)
                blog.link = entry.GetAlternateLink().href
                blog.category = [unicode(c.term, apps.encoding) for c in entry.category]
                blog.title = unicode(entry.title.text, apps.encoding)
                blog.blog_id = entry.id.text
                if entry.summary.text is not None:
                    blog.summary = unicode(entry.summary.text, apps.encoding)
                blog.put()
                
    def update_blog_post(self):
        all_token = OAuthService.all().filter('service_name =', blogger_service)
        for token in all_token:
            blogs = BlogSite.all().filter('user =', token.user).order('-updated')
            for blog in blogs:
                result = apps.get_data_from_signed_url(token.realm + blog.blog_id.split('-')[-1] + '/posts/default', token)
                d = feedparser.parse(result)
                blog.total_results = int(d.feed.totalresults)
                blog.put()
                for entry in d.entries:
                    add_post(entry, blog.user, blog.blog_id)
                    
    def import_blog_post(self):
        blogs = BlogSite.all().order('-updated')
        for blog in blogs:
            imported_cnt = apps.get_count(blog.user, blog.blog_id) 
            if imported_cnt == blog.total_results:
                apps.reset_counter(blog.user, '%s_start' % blog.blog_id)
                continue
            start = apps.get_count(blog.user, '%s_start' % blog.blog_id, init_value=1)
            token = OAuthService.all().filter('service_name =', blogger_service).filter('user =', blog.user).get()
            result = apps.get_data_from_signed_url(token.realm + blog.blog_id.split('-')[-1] + '/posts/default', token, **{'start-index':start})
            d = feedparser.parse(result)
            blog.total_results = int(d.feed.totalresults)
            blog.put()
            cnt = 0
            for entry in d.entries:
                add_post(entry, blog.user, blog.blog_id)
                cnt += 1
            apps.add_count(blog.user, '%s_start' % blog.blog_id, cnt)
            
    def post_to_blog(self):
        for twitter_blog in TwitterBlog.all().order('-created'):
            blog_id = twitter_blog.blog_id.split('-')[-1]
            token = OAuthService.all().filter('user =', twitter_blog.user).filter('service_name', 'blogger').get()
            blog_url = token.realm + blog_id + '/posts/default'
            today = datetime.today()
            curr_date = datetime(today.year, today.month, today.day)
            show_date = curr_date
            curr_date -= timedelta(seconds=apps.timedelta_seconds)
            path = os.path.join(os.path.dirname(__file__), 
                            'templates/%s/%s.html' % ('twitter', 'twitter_list'))
            contents = template.render(path, {'twitter_status':apps.get_twitter_daily(twitter_blog.user, curr_date)})
            entry = apps.make_blog_post('Twitter Daily(%s)' % (show_date.strftime('%Y-%m-%d')), contents, [twitter_blog.category])
            apps.get_data_from_signed_url(blog_url, token, 'POST', **{'body':entry})



def add_post(entry, user, blog_id):
    post = BlogPost.all().filter('post_id =', entry.id).get()
    if post is None:
        post = BlogPost(user=user)
        apps.add_count(user, blog_id, 1)
    if post.updated_b == entry.updated: return
    post.blog_id = blog_id
    post.post_id = entry.id
    if hasattr(entry, 'title'): post.title = entry.title
    if hasattr(entry, 'link'): post.link = db.Link(entry.link)
    if hasattr(entry,'tags'): post.category = [c.term for c in entry.tags]
    post.published = entry.published
    post.published_at = apps.datetime_format(entry.published)
    post.updated_b = entry.updated
    post.updated_at = apps.datetime_format(entry.updated)
    post.put()
    
def add_status(status, user):
    memcache.flush_all()
    update_twitter_user_flag = True
    for s in status:
        user_info = s['user']
        user_info = dict((k, v) for k, v in user_info.items())
        user_info['user_id'] = user_info['id']
        del user_info['id']
        twitter_user = memcache.get('twitter_%s' % user_info['user_id'])
        if update_twitter_user_flag and ((twitter_user is None) or twitter_user.statuses_count != user_info['statuses_count']):
            if twitter_user is None:
                twitter_user = TwitterUser.all().filter('user_id =',user_info['user_id']).get()
                if twitter_user is None:
                    twitter_user = TwitterUser(user=user)
            for k, v in user_info.items():
                twitter_user.__setattr__(k , v)
            twitter_user.put()
            memcache.add('twitter_%s' % user_info['user_id'], twitter_user)
            update_twitter_user_flag = False
        s = dict((str(k), v) for k, v in s.items())
        s['status_id'] = s['id']
        s['twitter_user_id'] = s['user']['id']
        del s['id']
        del s['user']
        s['published_at'] = datetime.strptime(s['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        twitter_status_user_id = 'twitter_status_%s' % s['status_id'] 
        if memcache.get(twitter_status_user_id) is None:
            twitter_entry = TwitterStatus.all().filter('status_id =', s['status_id']).get()
            if twitter_entry is None:
                twitter_entry = TwitterStatus(user=twitter_user.user, twitter_user=twitter_user, **s)
                twitter_entry.put()
                memcache.add(twitter_status_user_id, twitter_entry)
                apps.add_memcache_list(twitter_status_user_id)
                apps.counter_incr(twitter_status_counter, user)
# -*- coding: utf-8 -*-

'''
Created on 2009/05/20

@author: iBeyond
'''

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users
from google.appengine.ext.webapp import template
from google.appengine.ext import db
import apps
import logging
from gdata import service
import gdata
import gdata.alt.appengine
import atom
import atom.url
from apps import GoogleToken
from google.appengine.api import memcache

import cPickle as pickle

class Blogger(webapp.RequestHandler):
    service = 'blogger'
    next = 'http://aio.appspot.com/blogger/token'
#    next = 'http://i-nana.appspot.com/blogger/token'
    scopes = 'https://www.blogger.com/feeds/'
    @login_required
    def get(self, action=None):
        logging.info('### %s ###' % self.request.uri)
        self.user = users.get_current_user();
        self.write = self.response.out.write
        self.access_token = None
        self.page_data = apps.make_user_data(self)
        
        self.auth_token = GoogleToken.all().filter('user =', self.user).filter('service =', Blogger.service).get()
        self.blogger_service = service.GDataService(service=Blogger.service)
        gdata.alt.appengine.run_on_appengine(self.blogger_service)
        if action != 'token':
            if self.auth_token is None:
                self.redirect(service.GenerateAuthSubRequestUrl(Blogger.next, (Blogger.scopes), secure=False, session=True))
                return
            else:
                self.blogger_service.SetAuthSubToken(self.auth_token.token)
        if action:
            try:
                getattr(self, action)()
            except Exception, e:
                logging.exception(e)
            finally:
                pass
        self.page_data['blogger_list'] = BlogSite.all().filter('user =', self.user).order('-created')
        path = apps.get_template_path(__file__, 'index.html')
        self.write(template.render(path, self.page_data, debug=True))
    
    def update_blog(self):
        db.delete(BlogSite.all())
        query = service.Query()
        query.feed = Blogger.scopes + 'default/blogs'
        feed = self.blogger_service.GetFeed(query.ToUri())
        for entry in feed.entry:
            blog_id = entry.id.text
            blog_title = unicode(entry.title.text, apps.encoding)
            blog_category = [unicode(c.term,apps.encoding) for c in entry.category if c.term is not None]
            blog_site = BlogSite.all().filter('user =',self.user).filter('blog_id =', blog_id).get()
            blog_link = [(l.href) for l in entry.link]
            if blog_site:
                blog_site.title = blog_title
                blog_site.link = blog_link
                blog_site.updated = entry.updated.text
                blog_site.updated_at = apps.datetime_format(entry.updated.text)
                blog_site.published = entry.published.text
                blog_site.published_at = apps.datetime_format(entry.published.text)
                blog_site.category = blog_category
            else:
                blog_site = BlogSite(user=self.user,blog_id=blog_id)
                blog_site.title = blog_title
                blog_site.updated_at = apps.datetime_format(entry.updated.text)
                blog_site.published = entry.published.text
                blog_site.published_at = apps.datetime_format(entry.published.text)
                blog_site.category = blog_category
                blog_site.n_id = blog_id.split('-')[-1]
            blog_site.put()
            self.redirect('/blogger')
            
    def show_blog(self):
        blog_id = self.request.get('blog_id')
        if blog_id == '':
            self.redirect('/blogger')
            return
        print feed
        feed = self.blogger_service.GetFeed(Blogger.scopes + blog_id + '/posts/default')
        
        for entry in feed.entry:
            add_blog_entry(self.user,blog_id, entry)
        pass
    
    def token(self):
        token = gdata.auth.extract_auth_sub_token_from_url(self.request.uri)
        self.blogger_service.UpgradeToSessionToken(token)
        auth_token = GoogleToken.all().filter('user =', self.user).filter('service =',Blogger.service).get()
        if auth_token:
            auth_token.token = token
        else:
            auth_token = GoogleToken(user=self.user,service = Blogger.service, token=self.blogger_service.GetAuthSubToken())
        auth_token.put()
        self.redirect('/blogger')
   
class BlogSite(db.Model):
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    link = db.StringListProperty()
    updated = db.StringProperty()
    updated_at = db.DateTimeProperty()
    category = db.StringListProperty()
    published = db.StringProperty()
    published_at = db.DateTimeProperty()
    blog_id = db.StringProperty()
    title = db.StringProperty()
    n_id = db.StringProperty()
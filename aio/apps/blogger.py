# -*- coding: utf-8 -*-
import apps
from apps.stored import BlogSite, OAuthService, TwitterBlog
from google.appengine.ext import db
from gdata import service
import atom, gdata

service_name = 'blogger'

class Blogger(apps.AIOProcessor):
    
    def index(self):
        self.page_data['blogs'] = BlogSite.all().filter('user =', self.user).order('-updated')
        self.page_data['twitter_blog'] = TwitterBlog.all().filter('user =', self.user).get()
         
    def update_blog(self):
        token = OAuthService.all().filter('user =', self.user).filter('service_name =', service_name).get()
        if token:
            db.delete(BlogSite.all().filter('user =', self.user))
            result = apps.get_data_from_signed_url(token.realm + 'default/blogs', token)
            feed = atom.CreateClassFromXMLString(atom.Feed, result)
            for entry in feed.entry:
                blog = BlogSite(user=self.user)
                blog.link = entry.GetAlternateLink().href
                blog.category = [unicode(c.term, apps.encoding) for c in entry.category]
                blog.title = unicode(entry.title.text, apps.encoding)
                blog.blog_id = entry.id.text
                if entry.summary.text is not None:
                    blog.summary = unicode(entry.summary.text, apps.encoding)
                blog.put()
        self.redirect('/blogger')
    
    def make_default(self):
        key = self.request.get('blog')
        category = self.request.get('category')
        blog = db.get(key)
        db.delete(TwitterBlog.all().filter('user =', self.user))
        twitter_blog = TwitterBlog(user=self.user)
        twitter_blog.blog_id = blog.blog_id
        twitter_blog.category = category
        twitter_blog.put()
        self.redirect('/blogger')
        
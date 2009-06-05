# -*- coding: utf-8 -*-
import apps
from apps.stored import BlogSite, OAuthService, TwitterBlog, BlogPost
from google.appengine.ext import db
from gdata import service
import atom, gdata

service_name = 'blogger'

class Blogger(apps.AIOProcessor):
    
    def index(self):
        blogs = BlogSite.all().filter('user =', self.user).order('-updated')
        self.page_data['twitter_blog'] = TwitterBlog.all().filter('user =', self.user).get()
        self.page_data['blogs'] = blogs
        blog_id = self.request.get('blog_id')
        if blog_id == '': return
        self.page_data['posts'] = BlogPost.all().filter('blog_id =', blog_id).order('-updated_at').fetch(10)
        
    def new(self):
        blog_id = self.request.get('blog_id')
        if blog_id == '':
            self.redirect('/blogger')
            return
        self.page_data['blog_id'] = blog_id
        self.template_file = 'edit'
        
    def edit(self):
        post_id = self.request.get('post_id')
        if post_id == '':
            retrun
        token = OAuthService.all().filter('service_name =', service_name).filter('user =', self.user).get()
        post = BlogPost.all().filter('user =', self.user).filter('post_id =', post_id).get()
        url = token.realm + post.blog_id.split('-')[-1] + '/posts/' + post_id.split('-')[-1]
        result = apps.get_data_from_signed_url(token.realm + post.blog_id.split('-')[-1] + '/posts/default/' + post_id.split('-')[-1], token)
        from feedparser import feedparser
        d = feedparser.parse(result)
        self.page_data['post_title'] = d.entries[0].title
        self.page_data['post_content'] = d.entries[0].content[0].value
        
    def add(self):
        title = self.request.get('title')
        pass
    
    def delete(self):
        post_id = self.request.get('post_id')
        if post_id == '':
            self.redirect('/blogger')
            return
        token = OAuthService.all().filter('service_name =', service_name).filter('user =', self.user).get()
        post = BlogPost.all().filter('user =', self.user).filter('post_id =', post_id).get()
        blog_url = token.realm + post.blog_id.split('-')[-1] + '/posts/default/' + post_id.split('-')[-1]
        result = apps.get_data_from_signed_url(blog_url, token)
        apps.get_data_from_signed_url(blog_url, token, 'DELETE', **{'body':result})
        db.delete(post)
        apps.add_count(self.user, post.blog_id, -1)
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
        
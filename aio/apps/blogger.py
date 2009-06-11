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
        self.page_data['blog_id'] = self.request.get('blog_id')
        self.template_file = 'edit'
        blog_site = BlogSite.all().filter('blog_id =', blog_id).get()
        self.log.info(blog_site.category)
        self.page_data['category'] = blog_site.category
        self.page_data['action_title'] = 'New'
        
    def edit(self):
        token = OAuthService.all().filter('service_name =', service_name).filter('user =', self.user).get()
        post = BlogPost.all().filter('user =', self.user).filter('post_id =', self.request.get('post_id')).get()
        url = token.realm + post.blog_id.split('-')[-1] + '/posts/' + self.request.get('post_id').split('-')[-1]
        result = apps.get_data_from_signed_url(token.realm + post.blog_id.split('-')[-1] + '/posts/default/' + self.request.get('post_id').split('-')[-1], token)
        from feedparser import feedparser
        d = feedparser.parse(result)
        self.page_data['post_title'] = d.entries[0].title
        self.page_data['post_content'] = d.entries[0].content[0].value
        if hasattr(d.entries[0], 'tags'):
            self.page_data['post_tags'] = ','.join([tag.term for tag in d.entries[0].tags])
        self.page_data['action_title'] = 'Edit'  
        self.page_data['post_id'] = self.request.get('post_id')
        blog_site = BlogSite.all().filter('blog_id =', post.blog_id).get()
        self.page_data['category'] = blog_site.category
        
    def add(self):
        error = self.check_params()
        if not error:
            token = OAuthService.all().filter('user =', self.user).filter('service_name', service_name).get()
            blog_url = token.realm + self.form['blog_id'].split('-')[-1] + '/posts/default'
            entry = apps.make_blog_post(self.form['title'], self.form['content'], self.form['term'].split(','))
            apps.get_data_from_signed_url(blog_url, token, 'POST', **{'body':entry})
        else:
            self.log.info(error)
        self.redirect('/blogger')        
    
    def delete(self):
        error = self.check_params()
        if not error:
            token = OAuthService.all().filter('service_name =', service_name).filter('user =', self.user).get()
            post = BlogPost.all().filter('user =', self.user).filter('post_id =', self.form['post_id']).get()
            blog_url = token.realm + post.blog_id.split('-')[-1] + '/posts/default/' + self.form['post_id'].split('-')[-1]
            result = apps.get_data_from_signed_url(blog_url, token)
            apps.get_data_from_signed_url(blog_url, token, 'DELETE', **{'body':result})
            db.delete(post)
            apps.add_count(self.user, post.blog_id, -1)
        self.redirect('/blogger')

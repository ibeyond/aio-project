# -*- coding: utf-8 -*-
from apps.lib.aio import AIOProcessor
import apps
from apps.db import BlogSite, OAuthService, TwitterBlog, BlogPost
from google.appengine.ext import db
from gdata import service
import atom, gdata
from apps import lib
from apps.lib import oauth, feedparser

blogger_service = 'blogger'
blogger_post_counter = 'blogger_post'

def add_post(entry, user, blog_id):
    post = BlogPost.all().filter('post_id =', entry.id).get()
    if post is None:
        post = BlogPost(user=user)
        lib.counter_incr(blogger_post_counter, user)
    if post.updated_b == entry.updated: return
    post.blog_id = blog_id
    post.post_id = entry.id
    if hasattr(entry, 'title'): post.title = entry.title
    if hasattr(entry, 'link'): post.link = db.Link(entry.link)
    if hasattr(entry,'tags'): post.category = [c.term for c in entry.tags]
    post.published = entry.published
    post.published_at = lib.datetime_format(entry.published)
    post.updated_b = entry.updated
    post.updated_at = lib.datetime_format(entry.updated)
    post.put()
    
def make_blog_post(title, content, term):
    entry = gdata.GDataEntry()
    entry.title = atom.Title('xhtml', title)
    entry.content = atom.Content(content_type='html', text=content)
    entry.category = [atom.Category(term=category, scheme='http://www.blogger.com/atom/ns#') for category in term if category != '']
    return entry.ToString(apps.encoding)
class Blogger(AIOProcessor):
    
    def index(self):
        blogs = BlogSite.all().filter('user =', self.user).order('-updated_rss_at')
        self.page_data['twitter_blog'] = TwitterBlog.all().filter('user =', self.user).get()
        self.page_data['blogs'] = blogs
        blog_id = self.request.get('blog_id')
        if blog_id == '': return
        
    
    def post_list(self):
        blog_id = self.request.get('blog_id')
        if blog_id == '':
            self.redirect('/blogger')
            return
        self.page_data['blog'] = BlogSite.all().filter('blog_id =', blog_id).get()
        self.page_data['posts'] = BlogPost.all().filter('blog_id =', blog_id).order('-updated_at').fetch(10)
         
    def new(self):
        blog_id = self.page_data['blog_id'] = self.request.get('blog_id')
        self.template_file = 'edit'
        blog_site = BlogSite.all().filter('blog_id =', blog_id).get()
        self.page_data['category'] = blog_site.category
        self.page_data['action_title'] = 'New'
        
    def edit(self):
        token = lib.get_token(blogger_service, self.user)
        post = BlogPost.all().filter('user =', self.user).filter('post_id =', self.request.get('post_id')).get()
        url = token.realm + post.blog_id.split('-')[-1] + '/posts/' + self.request.get('post_id').split('-')[-1]
        result = oauth.get_data_from_signed_url(token.realm + post.blog_id.split('-')[-1] + '/posts/default/' + self.request.get('post_id').split('-')[-1], token)
        d = feedparser.parse(result)
        self.page_data['post_title'] = d.entries[0].title
        self.page_data['post_content'] = d.entries[0].content[0].value
        if hasattr(d.entries[0], 'tags'):
            self.page_data['post_tags'] = ','.join([tag.term for tag in d.entries[0].tags])
        self.page_data['action_title'] = 'Edit'  
        self.page_data['post_id'] = self.request.get('post_id')
        blog_site = BlogSite.all().filter('blog_id =', post.blog_id).get()
        self.page_data['category'] = blog_site.category
        
    def _add(self):
        error = self.check_params()
        if not error:
            token = lib.get_token(blogger_service, self.user)
            blog_url = token.realm + self.form['blog_id'].split('-')[-1] + '/posts/default'
            entry = make_blog_post(self.form['title'], self.form['content'], self.form['term'].split(','))
            result = oauth.get_data_from_signed_url(blog_url, token, 'POST', **{'body':entry})
            d = feedparser.parse(result)
            blog = BlogSite.all().filter('blog_id =', self.form['blog_id']).get()
            blog.total_results += 1
            blog.put()
            for entry in d.entries:
                add_post(entry, self.user, self.form['blog_id'])
        else:
            raise AIOException(error)
        self.redirect('/blogger')        
    
    def _delete(self):
        token = lib.get_token(blogger_service, self.user)
        post = BlogPost.all().filter('user =', self.user).filter('post_id =', self.form['post_id']).get()
        blog_url = token.realm + post.blog_id.split('-')[-1] + '/posts/default/' + self.form['post_id'].split('-')[-1]
        result = oauth.get_data_from_signed_url(blog_url, token)
        oauth.get_data_from_signed_url(blog_url, token, 'DELETE', **{'body':result})
        db.delete(post)
        lib.counter_decr(blogger_post_counter, self.user)
        self.redirect('/blogger')
        
    def _update_site(self):
        token = lib.get_token(blogger_service, self.user)
        result = oauth.get_data_from_signed_url(token.realm + 'default/blogs', token)
        feed = atom.CreateClassFromXMLString(atom.Feed, result)
        for entry in feed.entry:
            blog = BlogSite.all().filter('blog_id =', entry.id.text).get()
            if blog is None:
                blog = BlogSite(user=self.user)
            blog.link = entry.GetAlternateLink().href
            blog.category = [unicode(c.term, apps.encoding) for c in entry.category]
            blog.title = unicode(entry.title.text, apps.encoding)
            blog.blog_id = entry.id.text
            if entry.summary.text is not None:
                blog.summary = unicode(entry.summary.text, apps.encoding)
            blog.published = entry.published.text
            blog.published_at = lib.datetime_format(entry.published.text)
            blog.updated_rss = entry.updated.text
            blog.updated_rss_at = lib.datetime_format(entry.updated.text)
            blog.put()
        self.redirect('/blogger')
        
    def import_post(self):
        blog_id = self.request.get('blog_id')
        if blog_id == '':
            self.redirect('/blogger')
            return
        blog = BlogSite.all().filter('blog_id =', blog_id).get()
        if blog is None:
            slef.redirect('/blogger')
            return
        start = self.request.get('start')
        if start == '':
            start = 1
            del_flag = True
            while del_flag:
                posts = BlogPost.all().filter('blog_id =', blog_id) 
                if posts.count() >0 :
                    db.delete(posts)
                else:
                    del_flag = False
        
        token = lib.get_token(blogger_service, self.user)
        result = oauth.get_data_from_signed_url(token.realm + blog.blog_id.split('-')[-1] + '/posts/default', token, **{'start-index':start})
        d = feedparser.parse(result)
        blog.total_results = int(d.feed.totalresults)
        blog.put()
        end_flag = True
        for entry in d.entries:
            add_post(entry, blog.user, blog.blog_id)
            start = int(start) + 1
            end_flag = False
        if end_flag:
            start = -1
        self.page_data['start'] = start
        self.page_data['blog_id'] = blog_id

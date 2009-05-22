# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from apps.stored import OAuthService, TwitterUser
from apps.cron import Cron
import simplejson
import apps

class Twitter(apps.AIOProcessor):
    
    def get_twitter_user(self):
        twitter_user = TwitterUser.all().filter('user =', self.user).get()
        if twitter_user is None:
            c = Cron()
            c.twitter_update()
            twitter_user = TwitterUser.all().filter('user =', self.user).get()
        return twitter_user
        
    def index(self):
        #memcache.flush_all()
        twitter_user = self.get_twitter_user() 
        self.page_data['user_info'] = twitter_user
#        today = datetime.datetime.today();
#        curr_date = datetime.datetime(today.year,today.month,today.day)
#        self.page_data['local_now'] = curr_date
#        date_param = self.request.get('date') 
#        if  date_param != '':
#            self.page_data['date_param'] = date_param
#            curr_date = datetime.datetime(int(date_param.split('-')[0]),int(date_param.split('-')[1]),int(date_param.split('-')[2]))
#            self.page_data['time_links'] = [curr_date - datetime.timedelta(days=i) for i in range(1,8)]
#            curr_date -= datetime.timedelta(seconds=apps.timedelta_seconds)
#            
#            data = memcache.get('%s_%s' %(self.user.email() ,str(curr_date)))
#            if data is None:
#                data = TwitterStatus.all().filter('twitter_user =', self.page_data['user_info']).filter('published_at <', (curr_date + datetime.timedelta(days=1))).filter('published_at >=', curr_date).order('-published_at')
#                memcache.add('%s_%s' %(self.user.email() ,str(curr_date)), data)
#            self.page_data['twitter_status'] = data
#        else:
#            self.page_data['time_links'] = [curr_date - datetime.timedelta(days=i) for i in range(1,8)]
#            curr_date -= datetime.timedelta(seconds=apps.timedelta_seconds)
#            self.page_data['twitter_status'] = TwitterStatus.all().filter('twitter_user =', self.page_data['user_info']).filter('published_at <', (curr_date + datetime.timedelta(days=1))).filter('published_at >=', curr_date).order('-published_at')
#        twitter_blog = TwitterToBlog.all().filter('user =',self.user).filter('twitter_id =', str(self.page_data['user_info'].user_id)).get()
#        if twitter_blog:
#            self.page_data['twitter_blog_label'] = '%s_%s_%s' % (twitter_blog.twitter_id,twitter_blog.blog_n_id,twitter_blog.blog_label)

#    def index(self):
#        pass
#        request_token_url = ''
#        access_token_url = ''
#        user_auth_url = ''
#        
#        
#        twitter_max_count = 100
#        db_max_count = 10
#        twitter_status_counter = 'twitter_status'
#        def get(self, action=None):
#            self.access_token = None
#            self.page_data = apps.make_user_data(self)
#            
#            access_token = OAuthAccessToken.all().filter('user =', self.user).order('-created')
#            if access_token.count() > 0:
#                self.access_token = access_token.get()
#            if action is not None:
#                try:
#                    getattr(self, action)()
#                except Exception, e:
#                    logging.exception(e)
#                    self.redirect('/twitter')
#                finally:
#                    if action in ['token', 'clean',]: 
#                        self.redirect('/twitter')
#                        return
#                    elif action in ['show']:
#                        pass
#            else:
#                if self.access_token is None:
#                    for req_token in OAuthRequestToken.all():
#                        req_token.delete()
#                    token_info = apps.get_request_token_info(Twitter.request_token_url)
#                    request_token = OAuthRequestToken(
#                                                      user=self.user,
#                                                      service='twitter',
#                                                      **dict(token.split('=') for token in token_info.split('&'))
#                                                      )
#                    request_token.put()
#                    self.redirect(apps.get_signed_url(Twitter.user_auth_url, request_token))
#                    return
#                else:
#                    self.show()
#                    pass
#            from apps.blogger import BlogSite
#            self.page_data['blog_site'] = BlogSite.all().filter('user =', self.user)
#            path = apps.get_template_path(__file__, 'index.html')
#            self.write(template.render(path, self.page_data, debug=True))
#    
#    def post(self,action=None):
#        
#        if action is None:
#            self.redirect('/twitter')
#            return
#        self.user = users.get_current_user();
#        try:
#            getattr(self, action)()
#        except Exception, e:
#            logging.exception(e)
#            self.redirect('/twitter')
#            
#    def post_to_blog(self):
#        date_param = self.request.get('date_param')
#        logging.info(date_param)
#        post_date = datetime.datetime(int(date_param.split('-')[0]),int(date_param.split('-')[1]),int(date_param.split('-')[2]))
#        twitter_id = self.request.get('twitter_id')
#        twitter_blog = TwitterToBlog.all().filter('user =',self.user).filter('twitter_id', twitter_id).get()
#        apps.twitter_to_blog(post_date, twitter_blog)
#        self.redirect('/twitter/show?date=%s' % date_param)
#        pass
#    def link_blog(self):
#        if self.request.POST:
#            param = self.request.get('blog_label').split('_')
#            if param != '':
#                twitter_id = param[0]
#                blog_n_id = param[1]
#                blog_label = param[-1]
#                twitter_blog = TwitterToBlog.all().filter('user =',self.user).filter('twitter_id', twitter_id).get()
#                if twitter_blog:
#                    twitter_blog.blog_n_id = blog_n_id
#                    twitter_blog.blog_label = blog_label
#                else:
#                    twitter_blog = TwitterToBlog(user=self.user,twitter_id=twitter_id,blog_n_id=blog_n_id,blog_label=blog_label)
#                twitter_blog.put()
#        self.redirect('/twitter')
#    
    
#      
#        

#
#        
#    def clean(self):
#        db.delete(TwitterStatus.all().filter('user =', self.user).order('-status_id').fetch(500))
#        apps.reset_counter(self.user, self.twitter_status_counter)
#        from apps.cron import Cron
#        apps.reset_counter(self.user, Cron.twitter_import_counter)
        

#

#
#class TwitterToBlog(db.Model):
#    user = db.UserProperty()
#    created = db.DateTimeProperty(auto_now_add=True)
#    twitter_id = db.StringProperty()
#    blog_n_id = db.StringProperty()
#    blog_label = db.StringProperty() 
#        


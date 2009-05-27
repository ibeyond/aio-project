# -*- coding: utf-8 -*-
import apps
from apps import *
from apps.stored import OAuthService
from google.appengine.ext import db
import urllib

class Admin(apps.AIOProcessor):
    
    def index(self):
        service = OAuthService.all().filter('user =', self.user).filter('service_name =', 'blogger').get()
        logging.info(unicode(apps.get_data_from_signed_url('https://www.blogger.com/feeds/default/blogs', service),apps.encoding))
        self.page_data['site_list'] = apps.site_list
        self.page_data['oauth_service'] = OAuthService.all().filter('user =', self.user).order('-updated')
    
    def del_service(self):
        key = self.request.get('key')
        if key != '':
            db.delete(db.get(key))
        self.redirect('/admin')
        
    def get_token(self):
        key = self.request.get('key')
        if key == '':
            self.redirect('/admin')
            return
        service = db.get(key)
        kwargs = {}
        if service.service_name == 'blogger':
            kwargs['scope'] = 'https://www.blogger.com/feeds'
            #kwargs['oauth_callback'] = 'https://aio.appspot.com/admin/token?service=blogger'
            kwargs['oauth_callback'] = 'http://localhost/admin/token?service=blogger'
        token_info = apps.get_request_token_info(service, **kwargs)
        
        token_info = urllib.unquote(token_info)
        service.req_oauth_token = dict(token.split('=') for token in token_info.split('&'))['oauth_token']
        service.req_oauth_token_secret = dict(token.split('=') for token in token_info.split('&'))['oauth_token_secret']
        service.put()
        self.redirect(apps.get_signed_url(service.user_auth_url, service))
        return
    
    def token(self):
        service_name = self.request.get('service')
        service = OAuthService.all().filter('user =', self.user).filter('service_name =', service_name).get()
        token_info = apps.get_data_from_signed_url(service.access_token_url, service,**{'oauth_verifier':self.request.get('oauth_verifier')})
        token_info = urllib.unquote(token_info)
        service.oauth_token = dict(token.split('=') for token in token_info.split('&'))['oauth_token']
        service.oauth_token_secret = dict(token.split('=') for token in token_info.split('&'))['oauth_token_secret']
        if service.service_name == 'twitter':
            service.user_id = dict(token.split('=') for token in token_info.split('&'))['user_id']
        else:
            service.user_id = self.user.email()
        service.put()
        self.redirect('/admin')
        
    def add_service(self):
        error = self.check_params()
        result = {}
        result['message'] = 'success'
        if error:
            result['message'] = error
        else:
            service  = OAuthService.all().filter('user =', self.user).filter('service_name =', self.form['service_name']).get()
            if service:
                service.consumer_key = self.form['consumer_key']
                service.consumer_secret = self.form['consumer_secret']
            else:
                service = OAuthService(user=self.user,**self.form)
            service.put()
            result['contents'] = [service]
        self.result['body'] = result
            
#    def add_greader_shared_site(self):
#        if not self.request.POST:
#            return
#        user_id = self.request.get('user_id')
#        if user_id == '':
#            return
#        greader_shared_url = GReaderSharedUrl.all().filter('user =', self.user).get()
#        if greader_shared_url is None:
#            greader_shared_url = GReaderSharedUrl(user=self.user,user_id=user_id)
#        else:
#            greader_shared_url.user_id = user_id
#        greader_shared_url.put()
#        
#    def add_shared_site(self):
#        if not self.request.POST:
#            return
#        shared_name = self.request.get('shared_name')
#        shared_url = self.request.get('shared_url')
#        if shared_name == '' or shared_url == '':
#            return
#        shared_site = UserSharedSite.all().filter('user =',self.user).filter('name =',shared_name).get()
#        if shared_site is None:
#            shared_site = UserSharedSite(user=self.user,name=shared_name,url=shared_url)
#        else:
#            shared_site.url = shared_url
#        shared_site.put()
#        
#    def del_shared_site(self):
#        shared_name = self.request.get('shared_name')
#        if shared_name == '':
#            return
#        db.delete(UserSharedSite.all().filter('user =', self.user).filter('name =', shared_name).get())
#        
#    def add_keyword(self):
#        if not self.request.POST:
#            return
#        key_name = self.request.get('key_name')
#        key_value = self.request.get('key_value')
#        if key_name == '' or key_value == '':
#            return
#        keyword = Keyword.all().filter('user =', self.user).filter('name =', key_name).get()
#        if keyword is None:
#            keyword = Keyword(user=self.user,name=key_name,value=key_value)
#        else:
#            keyword.value = key_value;
#        keyword.put()
#        
#    def del_keyword(self):
#        key_name = self.request.get('key_name')
#        if key_name == '':
#            return
#        db.delete(Keyword.all().filter('user =', self.user).filter('name =', key_name).get())

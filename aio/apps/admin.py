# -*- coding: utf-8 -*-
import apps
from apps import *
from apps.stored import OAuthService
from google.appengine.ext import db
import urllib

class Admin(apps.AIOProcessor):
    
    def index(self):
        service = OAuthService.all().filter('user =', self.user).filter('service_name =', 'blogger').get()
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
            self.redirect('/admin')

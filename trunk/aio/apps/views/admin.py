# -*- coding: utf-8 -*-
from apps.lib.aio import AIOProcessor
from apps.lib.oauth import *
from apps.db import OAuthService
from google.appengine.ext import db
import urllib

services = {
            'blogger':{
                       'service_name' : 'blogger',
                       'realm' : 'https://www.blogger.com/feeds/',
                       'consumer_key' : 'aio.appspot.com',
                       'consumer_secret' : 'sLhPEOYV9DBcMeSTwmdZqbAC',
                       'request_token_url' : 'https://www.google.com/accounts/OAuthGetRequestToken',
                       'access_token_url' : 'https://www.google.com/accounts/OAuthGetAccessToken',
                       'user_auth_url' : 'https://www.google.com/accounts/OAuthAuthorizeToken',
                       },
            'twitter':{
                       'service_name' : 'twitter',
                       'realm' : 'https://twitter.com/',
                       'consumer_key' : 'VdAyDKInmaNXpbIJOTmLw',
                       'consumer_secret' : 'JqZsh6FGPPjYVdgypRYQbd0Ljl33kZ79EPJQ66pVKQ',
                       'request_token_url' : 'https://twitter.com/oauth/request_token',
                       'access_token_url' : 'https://twitter.com/oauth/access_token',
                       'user_auth_url' : 'https://twitter.com/oauth/authorize',
                       },
            }

class Admin(AIOProcessor):
    
    def index(self):
        self.page_data['oauth_service'] = OAuthService.all().filter('user =', self.user).order('-updated')
        self.page_data['oauth_service_list'] = services
    
    def _del_service(self):
        key = self.request.get('key')
        if key != '':
            db.delete(db.get(key))
        self.redirect('/admin')
        
    def _get_token(self):
        key = self.request.get('key')
        if key == '':
            self.redirect('/admin')
            return
        service = db.get(key)
        kwargs = {}
        kwargs['scope'] = service.realm
        kwargs['oauth_callback'] = '%s://%s/admin/token?service=%s' % (self.request.scheme, self.request.host, service.service_name)
        token_info = urllib.unquote(get_request_token_info(service, **kwargs))
        service.req_oauth_token = dict(token.split('=') for token in token_info.split('&'))['oauth_token']
        service.req_oauth_token_secret = dict(token.split('=') for token in token_info.split('&'))['oauth_token_secret']
        service.put()
        self.redirect(get_signed_url(service.user_auth_url, service))
        return
    
    def token(self):
        service_name = self.request.get('service')
        service = OAuthService.all().filter('user =', self.user).filter('service_name =', service_name).get()
        token_info = get_data_from_signed_url(service.access_token_url, service,**{'oauth_verifier':self.request.get('oauth_verifier')})
        token_info = urllib.unquote(token_info)
        service.oauth_token = dict(token.split('=') for token in token_info.split('&'))['oauth_token']
        service.oauth_token_secret = dict(token.split('=') for token in token_info.split('&'))['oauth_token_secret']
        if service.service_name == 'twitter':
            service.user_id = dict(token.split('=') for token in token_info.split('&'))['user_id']
        else:
            service.user_id = self.user.email()
        service.put()
        self.redirect('/admin')
        
    def _add_service(self):
        if self.request.method == 'POST':
            service  = OAuthService.all().filter('user =', self.user).filter('service_name =', self.form['service_name']).get()
            if service:
                service.consumer_key = services[self.form['service_name']]['consumer_key']
                service.consumer_secret = services[self.form['service_name']]['consumer_secret']
            else:
                service = OAuthService(user=self.user, **services[self.form['service_name']])
            service.put()
        else:
            pass
        self.redirect('/admin')

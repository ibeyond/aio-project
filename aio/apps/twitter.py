# -*- coding: utf-8 -*-
from google.appengine.api import memcache
from apps.stored import OAuthService, TwitterUser, TwitterStatus
from apps.cron import Cron
import simplejson
import apps
from datetime import datetime, timedelta

service_name = 'twitter'

class Twitter(apps.AIOProcessor):
    
    def get_twitter_user(self):
        twitter_user = TwitterUser.all().filter('user =', self.user).get()
        if twitter_user is None:
            Cron().twitter_update()
            twitter_user = TwitterUser.all().filter('user =', self.user).get()
        return twitter_user
        
    def index(self):
        memcache.flush_all()
        twitter_user = self.get_twitter_user() 
        self.page_data['user_info'] = twitter_user
        today = datetime.today();
        curr_date = datetime(today.year, today.month, today.day)
        self.page_data['local_now'] = curr_date
        date_param = self.request.get('date') 
        if  date_param != '':
            self.page_data['date_param'] = date_param
            curr_date = datetime(int(date_param.split('-')[0]),int(date_param.split('-')[1]),int(date_param.split('-')[2]))
            self.page_data['time_links'] = [curr_date - timedelta(days=i) for i in range(1,8)]
            curr_date -= timedelta(seconds=apps.timedelta_seconds)
            data = memcache.get('%s_%s' %(self.user.email() ,str(curr_date)))
            if data is None:
                data = TwitterStatus.all().filter('twitter_user =', self.page_data['user_info']).filter('published_at <', (curr_date + timedelta(days=1))).filter('published_at >=', curr_date).order('-published_at')
                memcache.add('%s_%s' %(self.user.email() ,str(curr_date)), data)
            self.page_data['twitter_status'] = data
        else:
            self.page_data['time_links'] = [curr_date - timedelta(days=i) for i in range(1,8)]
            curr_date -= timedelta(seconds=apps.timedelta_seconds)
            self.page_data['twitter_status'] = TwitterStatus.all().filter('twitter_user =', self.page_data['user_info']).filter('published_at <', (curr_date + timedelta(days=1))).filter('published_at >=', curr_date).order('-published_at')
            
    def post_to(self):
        token = OAuthService.all().filter('user =', self.user).filter('service_name =', service_name).get()
        if token:
            apps.get_data_from_signed_url('https://twitter.com/statuses/update.json', token, __meth='POST', **{'status':'测试一下客户端'})
        self.redirect('/twitter')
        pass
            
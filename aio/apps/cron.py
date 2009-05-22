## -*- coding: utf-8 -*-

from apps.stored import AIOBase, TwitterUser, OAuthService, TwitterStatus
from google.appengine.ext import webapp
from google.appengine.api import memcache
import simplejson
from datetime import datetime

import apps, logging


class Cron(webapp.RequestHandler):
    twitter_user_show_url = 'https://twitter.com/users/show.json'
    twitter_user_timeline_url = 'https://twitter.com/statuses/user_timeline.json'
    def get(self, action):
        getattr(self, action, self.index)()
        pass

    def index(self):
        self.redirect('/')
        
    def twitter_update(self):
        twitter_max_count = 10
        for local_user in AIOBase.all().order('-created'):
            service = OAuthService.all().filter('user =', local_user.user).filter('service_name =', 'twitter').get()
            if service is not None:
                twitter_user = TwitterUser.all().filter('user_id =',service.user_id).get()
                user_info = simplejson.loads(apps.get_data_from_signed_url(Cron.twitter_user_show_url, service, **{'user_id':service.user_id}))
                user_info = dict((str(k), v) for k, v in user_info.items())
                user_info['user_id'] = str(user_info['id'])
                if twitter_user is None:
                    twitter_user = TwitterUser(user=service.user, **user_info)

                else:
                    del user_info['id']
                    for k, v in user_info.items():
                        twitter_user.__setattr__(k , v)
                twitter_user.put()
                status = simplejson.loads(apps.get_data_from_signed_url(Cron.twitter_user_timeline_url, service, **{'count':twitter_max_count}), apps.encoding)
                add_status(status, service.user, twitter_user)
                
def add_status(status, user, twitter_user):
    logging.info(status)
    for s in status:
        s = dict((str(k), v) for k, v in s.items())
        s['status_id'] = s['id']
        s['twitter_user_id'] = s['user']['id']
        del s['user']
        s['published_at'] = datetime.strptime(s['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
        if memcache.get(str(s['status_id'])) is None:
            twitter_entry = TwitterStatus.all().filter('status_id =', s['id']).get()
            if twitter_entry is None:
                twitter_entry = TwitterStatus(user=user, twitter_user=twitter_user, **s)
                twitter_entry.put()
                memcache.add(str(s['status_id']), twitter_entry)
                apps.add_count(user, apps.twitter_status_counter, 1)
#        
#    def greader_import(self):
#        from apps.greader import GoogleReader
##        memcache.flush_all()
##        db.delete(GReaderSharedPost.all())
#        for local_account in LocalAccount.all():
##            apps.reset_counter(local_account.user,GoogleReader.service)
#            shared_url = apps.get_greader_shared_url(local_account.user)
#            if shared_url is None:
#                return
#            try:
#                result = urlfetch.fetch(shared_url)
#                if result.status_code == 200:
#                    import atom
#                    for entry in atom.CreateClassFromXMLString(atom.Feed, result.content).entry:
#                        post = memcache.get(str(entry.id.text))
#                        if post is None:
#                            shared_post =  GReaderSharedPost.all().filter('post_id =',str(entry.id.text)).get()
#                            if shared_post:
#                                db.delete(shared_post)
#                            shared_post = GReaderSharedPost()
#                            shared_post.post_id = str(entry.id.text)
#                            shared_post.user = local_account.user
#                            shared_post.title = unicode(str(entry.title.text), apps.encoding)
#                            shared_post.url = entry.link[0].href
#                            from google.appengine.ext.db import Text
#                            if entry.content is not None:
#                                shared_post.text = Text(entry.content.text,apps.encoding)
#                                import re
#                                p = re.compile(r'^<blockquote>Shared by .+? \n<br>\n(?P<comment>.+?)</blockquote>', re.IGNORECASE)
#                                if p.search(entry.content.text):
#                                    comment = p.search(entry.content.text).group('comment')
#                                    if comment:
#                                        shared_post.comment = unicode(comment,apps.encoding) 
#                            shared_post.published_at = apps.datetime_format(entry.published.text)
#                            shared_post.published = entry.published.text
#                            shared_post.put()
#                            apps.add_count(user=local_account.user,name=GoogleReader.service,count=1)
#                            memcache.add(str(entry.id.text),shared_post)
#            finally:
#                pass
#    

#    
#    def twitter_import(self):
#        for twitter_user in TwitterUser.all():
#            access_token = OAuthAccessToken.all().filter('user =', twitter_user.user).get()
#            if access_token is not None:
#                if (apps.get_count(twitter_user.user, Twitter.twitter_status_counter) < twitter_user.statuses_count):
#                    if ((apps.get_count(twitter_user.user, Cron.twitter_import_counter, init_value=2) - 1) * Cron.twitter_max_count) > twitter_user.statuses_count:
#                        if apps.get_count(twitter_user.user, Cron.twitter_import_counter) > 2:
#                            apps.reset_counter(twitter_user.user, Cron.twitter_import_counter)
#                    page_no = apps.get_count(user=twitter_user.user, name=Cron.twitter_import_counter, init_value=2)
#                    status = simplejson.loads(apps.get_data_from_signed_url(Twitter.user_timeline_url, access_token, **{'page':page_no, 'count':5}), apps.encoding)
#                    apps.add_status(status, access_token.user, twitter_user)
#                    apps.add_count(twitter_user.user, Cron.twitter_import_counter, 1)
#                else:
#                    apps.reset_counter(twitter_user.user, Cron.twitter_import_counter)
#                    
#    def twitter_to_blog(self):
#        pass
##        from apps.twitter import TwitterToBlog
##        for twitter_blog in TwitterToBlog.all():
##            date = datetime.today() - timedelta(days=1)
##            apps.twitter_to_blog(date, twitter_blog)
#
#    def test(self):
#        for twitter_user in TwitterUser.all():
#            access_token = OAuthAccessToken.all().filter('user =', twitter_user.user).get()
#            if access_token is not None:
#                self.response.out.write(simplejson.dumps(apps.send_to_twitter('https://twitter.com/statuses/update.json',access_token,**{'status':'不追加头[X-Twitter-Client],会正常显示source吗？'}),apps.encoding))
#            
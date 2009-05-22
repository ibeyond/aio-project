# -*- coding: utf-8 -*-

from google.appengine.api import users
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp import template
from google.appengine.api import memcache
from google.appengine.ext import db
from appengine_utilities import sessions
from random import getrandbits
from time import time
from hmac import new as hmac
from urllib import urlencode, quote as urlquote
from hashlib import sha1
from datetime import datetime,timedelta
from apps.stored import AIOBase, Counter
import simplejson, os, logging, re

site_list = ['twitter','blogger']

twitter_status_counter = 'twitter_status'

google_consumer_key = 'aio.appspot.com'
google_consumer_secret = 'sLhPEOYV9DBcMeSTwmdZqbAC'

encoding = 'utf-8'

timedelta_seconds = 28800

class AIOProcessor(webapp.RequestHandler):
    """
    除Home页外，其他所有处理页的基类
    """
    @login_required
    def get(self,action='index'):
        logging.info('### %s ###' % self.request.uri)
        memcache.flush_all()
        self.log = logging
        if action == '':
            action = 'index'
        self.user = users.get_current_user()
        reg_account(self.user)
        self.page_data = {}
        self.page_data['user'] = self.user
        self.page_data['logout_url'] = users.create_logout_url('/')
        self.session = sessions.Session()
        self.redirect_url = None
        try:
            getattr(self,action)()
        except Exception, e:
            logging.exception(e)
#            self.redirect('/error')
        finally:
            pass
        self.page_data['session'] = self.session
        path = os.path.join(os.path.dirname(__file__), 
                            'templates/%s/%s.html' % (self.__class__.__name__.lower(), action))
        try:
            self.response.out.write(template.render(path, self.page_data))
        except:
            path = os.path.join(os.path.dirname(__file__), 
                            'templates/%s/%s.html' % (self.__class__.__name__.lower(), 'index'))
            self.response.out.write(template.render(path, self.page_data))
        
        pass
        
    def post(self,action):
        logging.info('### %s ###' % self.request.uri)
        self.log = logging
        self.form = dict((str(arg),self.request.get(arg))for arg in self.request.arguments())
        self.write = self.response.out.write
        self.user = users.get_current_user()
        self.result = {}
        self.result['type'] = 'json' 
        try:
            getattr(self, action)()
            if self.result['type'] == 'json':
                self.response.headers['Content-Type'] ='application/json;charset=%s' % encoding
                self.write(self.dumps(self.result['body']))
            else:
                if self.result['type'] == 'html':
                    self.response.headers['Content-Type'] ='application/html;charset=%s' % encoding
                else:
                    self.response.headers['Content-Type'] ='application/%s' % self.response_type
                self.write(self.result['body'])
        except Exception, e:
            logging.exception(e)
            self.redirect(self.__class__.__name__.lower())
        finally:
            pass
    
    def index(self):
        self.redirect('/')
        
    def dumps(self,result):
        logging.info(simplejson.dumps(result, cls=ComplexEncoder, encoding=encoding))
        return simplejson.dumps(result, cls=ComplexEncoder, encoding=encoding)
    
    def check_params(self, exclude=[]):
        return ['\n%s 为必填项' % k for k,v in self.form.items() if v=='' and k not in exclude]

class Error(AIOProcessor):
    def get(self):
        print 'error page'

def db_to_dict(obj, exclude_key=[]):
    """
    将db.model类型数据转换为dict
    """
    __to_dict = lambda obj:dict((att, obj.__getattribute__(att)) for att in dir(obj) if (not callable(getattr(obj, att))) and (not att.startswith('_')) and (att not in exclude_key))
    if isinstance(obj, list):
        return [__to_dict(o) for o in obj]
    else:
        return __to_dict(obj) 

def obj_to_dict(obj, exclude_key=[]):
    """
    将Object转换为dict
    """
    return dict((att, getattr(obj, att)()) for att in dir(obj) if callable(getattr(obj, att)) and (not att.startswith('_')) and (att not in exclude_key))

class ComplexEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        from datetime import datetime
        from google.appengine.ext import db
#        logging.info('obj.type = %s' % type(obj))
        if isinstance(obj, datetime):
            return str(obj)
        elif isinstance(obj, users.User):
            return obj_to_dict(obj)
        elif issubclass(obj.__class__, db.Model):
            return db_to_dict(obj)
        elif isinstance(obj, db.Query):
            pass
        else:
            return super(ComplexEncoder, self).default(obj)

def reg_account(user):
    """
    注册本站用户
    """
    account = memcache.get(user.email())
    if account is None:
        if not AIOBase.all().filter('user =', user).get():
            account = AIOBase(user=user).put()
            memcache.add(user.email(), account)

def get_request_token_info(__service):
    return get_data_from_signed_url(__service.request_token_url,__service)

def get_data_from_signed_url(__url, __service, __meth='GET', **extra_params):
    if __meth != 'GET':
        headers = get_auth_headers(__url, __service, __meth, **extra_params)
        method = urlfetch.POST
        return urlfetch.fetch(url=__url,payload=urlencode(extra_params),method=method, headers=headers).content
    else:
        return urlfetch.fetch(get_signed_url(__url, __service, __meth, **extra_params)).content

def get_signed_url(__url, __service, __meth='GET', **extra_params):
    kwargs = {
        'oauth_consumer_key': __service.consumer_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version': '1.0',
        'oauth_timestamp': int(time()),
        'oauth_nonce': getrandbits(64),
        }
    kwargs.update(extra_params)
    key = '%s&' % encode(__service.consumer_secret)
    if __service.oauth_token is not None:
        kwargs['oauth_token'] = __service.oauth_token
        key += encode(__service.oauth_token_secret)
    elif __service.req_oauth_token is not None:
        kwargs['oauth_token'] = __service.req_oauth_token
        key += encode(__service.req_oauth_token_secret)
    
           
    message = '&'.join(map(encode, [
        __meth.upper(), __url, '&'.join(
            '%s=%s' % (encode(k), encode(kwargs[k])) for k in sorted(kwargs)
            )
        ]))
    kwargs['oauth_signature'] = hmac(
        key, message, sha1
        ).digest().encode('base64')[:-1]
#    logging.info('#### [%s] ####' % '%s?%s' % (__url, urlencode(kwargs)))
    return '%s?%s' % (__url, urlencode(kwargs))

def get_auth_headers(__url,__service, __meth='GET', **params):
    message_info = get_signed_url(__url, __service, __meth, **params)
    auth = ','.join(message_info.split('?')[1].split('&'))
    return {'Authorization':'OAuth realm="%s",%s' % (__service.realm, auth)}


def encode(text):
    return urlquote(str(text), '')

def add_count(user, name, count):
    counter = Counter.all().filter('user =', user).filter('name =', name).get()
    if counter is None:
        counter = Counter(user=user, name=name, value=count)
    else:
        counter.value += count
    counter.put()
    
def get_count(user, name, init_value=0):
    counter = Counter.all().filter('user =', user).filter('name =', name).get()
    if counter is None:
        counter = Counter(user=user, name=name, value=init_value)
        counter.put()
    return counter.value

def reset_counter(user, name):
    db.delete(Counter.all().filter('user =', user).filter('name =', name))
      
class UserSharedSite(db.Model):
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    name = db.StringProperty()
    url = db.StringProperty()  
    
class Keyword(db.Model):
    user = db.UserProperty()
    name = db.StringProperty()
    value = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)

class GReaderSharedPost(db.Model):
    user =db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    post_id = db.StringProperty(multiline=True)
    title = db.StringProperty()
    url = db.StringProperty()
    comment = db.StringProperty(multiline=True)
    text = db.TextProperty()
    published_at = db.DateTimeProperty()
    published = db.StringProperty() 

class GReaderSharedUrl(db.Model):
    user = db.UserProperty()
    user_id = db.StringProperty()

def datetime_format(source):
    """格式化时间"""
    last_datetime = re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', source)[0]
    last_time_offset = re.findall(r'[Z]|[+|-]{1}\d{2}', source)[0]
    last_updated_date_time = datetime.strptime(last_datetime.replace('T',' '),"%Y-%m-%d %H:%M:%S")
    if last_time_offset != 'Z':
        last_updated_date_time = last_updated_date_time + timedelta(hours=int(last_time_offset[1:3]))
    return last_updated_date_time   

def get_greader_shared_url(user):
    from apps.greader import GoogleReader 
    greader_url = GReaderSharedUrl.all().filter('user =', user).get()
    if greader_url:
        return GoogleReader.greader_prefix + greader_url.user_id + GoogleReader.greader_suffix
    else:
        return None 

class GoogleToken(db.Model):
    user = db.UserProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    service = db.StringProperty()
    token = db.StringProperty()
    
    
def twitter_to_blog(date, twitter_blog):
    from apps.blogger import Blogger
    import gdata
    import atom
    from gdata import service
    last_time = date - timedelta(seconds=timedelta_seconds)
    from apps.twitter import TwitterStatus 
    twitter_list = TwitterStatus.all().filter('user =',twitter_blog.user).filter('published_at <', (last_time + timedelta(days=1))).filter('published_at >=', last_time).order('published_at')
    entry = gdata.GDataEntry()
    entry.title = atom.Title('xhtml', u'Twitter %s-%s-%s' % (date.year,date.month,date.day))
    from google.appengine.ext.webapp import template
    path = get_template_path(__file__, '../twitter/twitter_to_blog.html')
    entry.content = atom.Content(content_type='html', text=template.render(path, {'twitter_status':twitter_list}))
    entry.category = [atom.Category(term='twitter',scheme='http://www.blogger.com/atom/ns#')]
    date += timedelta(days=1)
    temp = str(date)[:10] + 'T' + str(date)[11:-3] + '+08:00'
    if len(str(date))<23:
        temp = str(date)[:10] + 'T' + str(date)[11:] + '.000+08:00'
    entry.published= atom.Published(temp)
    auth_token = GoogleToken.all().filter('user =', twitter_blog.user).filter('service =', Blogger.service).get()
    
    blogger_service = service.GDataService(service=Blogger.service)
    print '\n'.join(['%s = %s' % (attr, getattr(blogger_service,attr)) for attr in dir(blogger_service)])
    gdata.alt.appengine.run_on_appengine(blogger_service)
    blogger_service.SetAuthSubToken(auth_token.token)
    logging.info(auth_token.token)
    blogger_service.Post(entry, Blogger.scopes + '%s/posts/default' % twitter_blog.blog_n_id)
    
    
    
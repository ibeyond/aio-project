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
        except Exception, e:
            logging.exception(e)
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
        self.result['body'] = None  
        try:
            getattr(self, action)()
            if self.result['type'] == 'json':
                self.response.headers['Content-Type'] ='application/json;charset=%s' % encoding
                if self.result['body'] is not None: self.write(self.dumps(self.result['body']))
            else:
                self.response.headers['Content-Type'] ='application/%s; charset=%s' % (self.result['type'] ,encoding)
                if self.result['body'] is not None: self.write(self.result['body'])
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

def get_request_token_info(__service, __meth='GET', **extra_params):
    return get_data_from_signed_url(__service.request_token_url,__service, __meth, **extra_params)

def get_data_from_signed_url(__url, __service, __meth='GET', **extra_params):
    if __service.service_name == 'twitter' and __meth == 'GET':
        return urlfetch.fetch(get_signed_url(__url, __service, __meth, **extra_params)).content
    if __service.oauth_token is not None:
        method = urlfetch.POST
        if __meth == 'GET':
            method = urlfetch.GET
        headers = get_auth_headers(__url, __service, __meth, **extra_params)
        if __service.realm == 'https://www.blogger.com/feeds/':
            headers['Content-Type'] = 'application/atom+xml'
        if extra_params['body'] is not None:
            logging.info(urlquote(extra_params['body']))
            logging.info(extra_params['body'])
            return urlfetch.fetch(url=__url,payload=extra_params['body'],method=method, headers=headers).content
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
    return '%s?%s' % (__url, urlencode(kwargs))

def get_auth_headers(__url,__service, __meth='GET', **params):
    message_info = get_signed_url(__url, __service, __meth, **params)
    auth = ', '.join(message_info.split('?')[1].split('&'))
    logging.info({r'Authorization':'OAuth realm=%s, %s' % (str(__service.realm), str(auth))})
    return {'Authorization':'OAuth realm="%s",%s' % (__service.realm, auth)}


def encode(text):
    return urlquote(str(text), '')

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


def datetime_format(source):
    """格式化时间"""
    last_datetime = re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', source)[0]
    last_time_offset = re.findall(r'[Z]|[+|-]{1}\d{2}', source)[0]
    last_updated_date_time = datetime.strptime(last_datetime.replace('T',' '),"%Y-%m-%d %H:%M:%S")
    if last_time_offset != 'Z':
        last_updated_date_time = last_updated_date_time + timedelta(hours=int(last_time_offset[1:3]))
    return last_updated_date_time   


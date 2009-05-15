
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch as urlfetch
from random import getrandbits
from time import time
from hmac import new as hmac
from urllib import urlencode, quote as urlquote
from hashlib import sha1

import simplejson

import os

import logging

consumer_key = 'VdAyDKInmaNXpbIJOTmLw'
consumer_secret = 'JqZsh6FGPPjYVdgypRYQbd0Ljl33kZ79EPJQ66pVKQ'

encoding = 'utf-8'

def make_user_data(obj):
    if not hasattr(obj,'page_data'): obj.page_data = {}
    if hasattr(obj,'user') and obj.user:
        obj.page_data['user'] = obj.user
        obj.page_data['logout_url'] = users.create_logout_url('/')
    else:
        obj.page_data['login_url'] = users.create_login_url('/')
    if hasattr(obj,'session'): obj.page_data['session'] = obj.session
    return obj.page_data
    
def get_template_path(app_name, template_name, template_base='templates'):
    return os.path.join(os.path.dirname(app_name), '/'.join((template_base, app_name.split(os.sep)[-1].split('.')[0], template_name)))


def get_request_token_info(__url):
    return get_data_from_signed_url(__url)

def get_data_from_signed_url(__url, __token=None, __meth='GET', **extra_params):
    return urlfetch(get_signed_url(__url, __token, __meth, **extra_params)).content

def get_signed_url(__url, __token=None, __meth='GET', **extra_params):

    kwargs = {
        'oauth_consumer_key': consumer_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version': '1.0',
        'oauth_timestamp': int(time()),
        'oauth_nonce': getrandbits(64),
        }

    kwargs.update(extra_params)
    key = '%s&' % encode(consumer_secret)
    if __token is not None:
        kwargs['oauth_token'] = __token.oauth_token
        key += encode(__token.oauth_token_secret) 
    message = '&'.join(map(encode, [
        __meth.upper(), __url, '&'.join(
            '%s=%s' % (encode(k), encode(kwargs[k])) for k in sorted(kwargs)
            )
        ]))
    kwargs['oauth_signature'] = hmac(
        key, message, sha1
        ).digest().encode('base64')[:-1]
    return '%s?%s' % (__url, urlencode(kwargs))

def encode(text):
    return urlquote(str(text), '')

def db_to_dict(obj, exclude_key=[]):
    __to_dict = lambda obj:dict((att, obj.__getattribute__(att)) for att in dir(obj) if (not callable(getattr(obj, att))) and (not att.startswith('_')) and (att not in exclude_key))
    if isinstance(obj, list):
        return [__to_dict(o) for o in obj]
    else:
        return __to_dict(obj) 

def model_to_dict(obj, exclude_key=[]):
    return dict((att, getattr(obj, att)()) for att in dir(obj) if callable(getattr(obj, att)) and (not att.startswith('_')) and (att not in exclude_key))

class ComplexEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        from datetime import datetime
        from google.appengine.ext import db
#        logging.info('obj.type = %s' % type(obj))
        if isinstance(obj, datetime):
            return str(obj)
        elif isinstance(obj, users.User):
            return model_to_dict(obj)
        elif issubclass(obj.__class__, db.Model):
            return db_to_dict(obj)
        elif isinstance(obj, db.Query):
            pass
        else:
            return super(ComplexEncoder, self).default(obj)

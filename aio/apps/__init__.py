
from google.appengine.api import users
from google.appengine.api.urlfetch import fetch as urlfetch
from random import getrandbits
from time import time
from hmac import new as hmac
from urllib import urlencode, quote as urlquote
from hashlib import sha1

import os

import logging

consumer_key = 'VdAyDKInmaNXpbIJOTmLw'
consumer_secret = 'JqZsh6FGPPjYVdgypRYQbd0Ljl33kZ79EPJQ66pVKQ'

def make_user_data(page_data={}):
    user = users.get_current_user()
    if user:
        page_data['user'] = user
        page_data['logout_url'] = users.create_logout_url('/')
    else:
        page_data['login_url'] = users.create_login_url('/')
    return page_data
    
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

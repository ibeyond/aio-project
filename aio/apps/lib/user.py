# -*- coding: utf-8 -*-

'''
Created on Jun 12, 2009

@author: SongQingJie
'''

from apps.db import AIOBase
from google.appengine.api import memcache

def get_user(email):
    """
    根据电子邮件地址取得用户
    """
    user = memcache.get(email)
    if user is None:
        user = AIOBase.all().filter('user.email =', email).get().user
        memcache.add(email, user)
        add_memcache_list(email)
    return user

def reg_account(user):
    """
    注册本站用户
    """
    account = memcache.get('aio_user_%s' % user.email())
    if account is None:
        if not AIOBase.all().filter('user =', user).get():
            account = AIOBase(user=user)
            account.put()
            memcache.add('aio_user_%s' % user.email(), account)
# -*- coding: utf-8 -*-

'''
Created on Jun 12, 2009

@author: SongQingJie
'''

from google.appengine.api import memcache
from apps.db import *

import logging

def datetime_format(source):
    """格式化时间"""
    last_datetime = re.findall(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', source)[0]
    last_time_offset = re.findall(r'[Z]|[+|-]{1}\d{2}[:]\d{2}$', source)[0]
    last_updated_date_time = datetime.strptime(last_datetime.replace('T',' '),"%Y-%m-%d %H:%M:%S")
    if last_time_offset != 'Z':
        last_updated_date_time = last_updated_date_time + timedelta(hours=int(last_time_offset[1:3]))
    return last_updated_date_time   

def add_memcache_list(name):
    """
    添加非计数器缓存列表
    """
    memcache_list = memcache.get(r'memcache_list')
    if memcache_list is None:
        memcache_list = [name]
    else:
        memcache_list.append(name)
    memcache.add(r'memcache_list', memcache_list)
    
def counter_incr(counter_name, user, delta=1):
    """
    计数器累加
    """
    counter_name = r'counter^%s^for^%s' % (counter_name, user.email())
    if memcache.incr(counter_name, delta) is None:
        memcache.set(counter_name, add_count(user, counter_name.split('^')[1], delta=delta))
    counter_list = memcache.get(r'aio_counter_list')
    if (counter_list is not None) and (counter_name not in counter_list):
        counter_list.append(counter_name)
    else:
        counter_list = [counter_name]
    memcache.add(r'aio_counter_list', counter_list)
    return memcache.get(counter_name)


def add_count(user, name, delta=1):
    """
    计数器写入数据库
    """
    counter = Counter.all().filter('user =', user).filter('name =', name).get()
    if counter is None:
        counter = Counter(user=user, name=name, value=delta)
    else:
        counter.value += delta
    counter.put()
    return counter.value

def get_count(user, name):
    """
    取得计数值
    """
    counter_name = r'counter^%s^for^%s' %(name, user.email())
    counter_value = memcache.get(counter_name)
    if counter_value is None:
        counter = Counter.all().filter('user =', user).filter('name =', name).get()
        if counter is None:
            counter_value = add_counter(user, counter_name.split('^')[1],delta=0)
        else:
            counter_value = counter.value
        memcache.set(counter_name,counter_value)
    return counter_value

def reset_counter(user, name):
    """
    重置计数器
    """
    db.delete(Counter.all().filter('user =', user).filter('name =', name))
    memcache.delete(r'counter^%s^for^%s' %(name, user.email()))
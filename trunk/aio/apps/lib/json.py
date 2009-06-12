# -*- coding: utf-8 -*-
'''
Created on Jun 12, 2009

@author: SongQingJie
'''

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

# -*- coding: utf-8 -*-

'''
Created on Jun 11, 2009

@author: SongQingJie
'''
import logging, os

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import login_required
from google.appengine.ext.webapp import template
from google.appengine.api import users


from appengine_utilities import sessions

import apps

class AIOException(Exception):
    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg
    
    def __str__(self):
        if isinstance(self.message, list):
            return '<br />'.join(self.message)
        else:
            return self.message

class AIOProcessor(webapp.RequestHandler):
    def __init(self):
        logging.info('### %s ###' % self.request.uri)
        self.write = self.response.out.write
        self.log = logging
        #取得当前用户
        self.user = users.get_current_user()
    """
    AIO处理器，一个简单的框架
    """
    @login_required
    def get(self,action='index'):
        self.__init()
        if action == '':
            action = 'index'
        #以_开头的方法都为Post方法
        if action.startswith('_'):
            self.error_page('非法访问')
            return
        #初始化页面数据
        self.page_data = {}
        if self.user.email() != 'ibeyond@gmail.com':
            self.error_page('非法访问')
            return
        self.page_data['user'] = self.user
        
        self.page_data['logout_url'] = users.create_logout_url('/')
        self.session = sessions.Session()
        self.template_file = None
        try:
            getattr(self,action)()
            self.page_data['session'] = self.session
            path = os.path.join(os.path.dirname(__file__), 
                        '../views/templates/%s/%s.html' % (self.__class__.__name__.lower(), (self.template_file is None) and action or self.template_file))
            self.log.info(path)
            self.write(template.render(path, self.page_data))
        except Exception, e:
            self.log.exception(e)
            self.error_page(e)
            return 
        
    def post(self,action):
        """
        所有的Post方法必须以_开头
        """
        self.__init()
        self.form = dict((str(arg),self.request.get(arg))for arg in self.request.arguments())
        self.result = {}
        self.result['type'] = 'json'
        self.result['body'] = None  
        try:
            getattr(self, action)()
            self.response.headers['Content-Type'] ='application/%s; charset=%s' % (self.result['type'], apps.encoding)
            if self.result['body'] is not None:
                if self.result['type'] == 'json':
                    self.write(self.dumps(self.result['body']))
                else:
                    self.write(self.result['body'])
        except Exception, e:
            self.log.exception(e)
            self.error_page(e)
    
    def error_page(self,msg):
        self.write(msg) 
    
    def check_params(self, exclude=[]):
        return ['\n%s 为必填项' % k for k,v in self.form.items() if v=='' and k not in exclude]
        
    def dumps(self,result):
        return simplejson.dumps(result, cls=ComplexEncoder, encoding=encoding)
# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from datetime import datetime
import logging
'''
Created on 2009/05/14

@author: iBeyond
'''

class Cron(webapp.RequestHandler):
    '''
    classdocs
    '''


    def get(self):
        logging.info('cron task start: [%s]' % datetime.now())
        pass
        
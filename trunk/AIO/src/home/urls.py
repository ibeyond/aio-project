# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('home.views',
    (r'^token_list/$', 'token_list'),
    (r'^$', 'index'),
    (r'^setting/$', 'setting'),
    (r'^retrieve_token/$', 'retrieve_token'),
)

# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('blogsearch.views',
    (r'^$', 'index'),
)

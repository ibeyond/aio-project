# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^blogsearch/', include('blogsearch.urls')),
)

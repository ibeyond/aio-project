# -*- coding: utf-8 -*-

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from apps.db import Keyword
import logging, re, apps
from datetime import timedelta

register = webapp.template.create_template_register()
@register.filter
def datetz(date, arg):
    t=timedelta(seconds=apps.timedelta_seconds)
    return webapp.template.django.template.defaultfilters.date(date+t, arg)

@register.filter
def replace_link (str):
    """
    将Url地址替换为Link
    """
    p = re.compile(r'(?P<name>(http|https)://\S+\b)')
    str = p.sub('(<a href="\g<1>" title="\g<1>">url</a>)',str)
    for keyword in Keyword.all().filter('keyword_category =','url'):
        p = re.compile(r'(?P<name>\b%s\b(?![.]))' % keyword.keyword_name, re.IGNORECASE)
        str = p.sub('<a href="%s">\g<1></a>' % keyword.keyword_value,str)
    return str

@register.filter
def replace_twitter_link (str):
    """
    替换Twitter用户名为Link
    """
    p = re.compile(r'@(?P<name>\w+\b)')
    str = p.sub('<a href="https://twitter.com/\g<1>">@\g<1></a>',str)
    return str
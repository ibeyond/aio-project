# -*- coding: utf-8 -*-
import re
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

register = webapp.template.create_template_register()

import logging
import apps


@register.filter
def datetz(date, arg):
    from apps.twitter import Twitter
    from datetime import timedelta
    t=timedelta(seconds=apps.timedelta_seconds)
    return webapp.template.django.template.defaultfilters.date(date+t, arg)

@register.filter
def replace_link (str):
    p = re.compile(r'(?P<name>(http|https)://\S+\b)')
    str = p.sub('(<a href="\g<1>" title="\g<1>">url</a>)',str)
    p = re.compile(r'@(?P<name>\w+\b)')
    str = p.sub('@<a href="https://twitter.com/\g<1>">\g<1></a>',str)
    from apps import Keyword
    for keyword in Keyword.all():
        p = re.compile(r'(?P<name>\b%s\b(?![.]))' % keyword.name, re.IGNORECASE)
        str = p.sub('<a href="%s">\g<1></a>' % keyword.value,str)
    return str
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from apps.views.home import Home

from apps.views import twitter
from apps.lib.cron import Cron
from apps.views.admin import Admin
from apps.views.blogger import Blogger
from apps.views.keyword import Keyword

webapp.template.register_template_library('apps.views.tags') 

urls = [
        (r'/', Home),
        (r'/twitter', twitter.Twitter),
        (r'/twitter/(.*)', twitter.Twitter),
        (r'/blogger', Blogger),
        (r'/blogger/(.*)', Blogger),
        (r'/keyword', Keyword),
        (r'/keyword/(.*)', Keyword),
        (r'/admin', Admin),
        (r'/admin/(.*)', Admin),
        (r'/cron/(.*)', Cron),
        ]

application = webapp.WSGIApplication(urls, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from apps.home import Home

from apps.twitter import Twitter
from apps.cron import Cron
from apps.admin import Admin
from apps.clean import Clean
from apps.blogger import Blogger
from apps.keyword import Keyword

webapp.template.register_template_library('apps.tags') 

urls = [
        (r'/', Home),
        (r'/twitter', Twitter),
        (r'/twitter/(.*)', Twitter),
        (r'/blogger', Blogger),
        (r'/blogger/(.*)', Blogger),
        (r'/keyword', Keyword),
        (r'/keyword/(.*)', Keyword),
        (r'/admin', Admin),
        (r'/admin/(.*)', Admin),
        (r'/cron/(.*)', Cron),
        (r'/clean', Clean),
        ]

application = webapp.WSGIApplication(urls, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

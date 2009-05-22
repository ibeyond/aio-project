from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from apps.home import Home
from apps import Error
from apps.twitter import Twitter
from apps.cron import Cron
from apps.admin import Admin
#from apps.greader import GoogleReader
#from apps.blogger import Blogger

webapp.template.register_template_library('apps.tags') 

urls = [
        (r'/', Home),
        (r'/twitter', Twitter),
        (r'/twitter/(.*)', Twitter),
#        (r'/greader', GoogleReader),
#        (r'/greader/(.*)', GoogleReader),
#        (r'/blogger', Blogger),
#        (r'/blogger/(.*)', Blogger),
        (r'/admin', Admin),
        (r'/admin/(.*)', Admin),
        (r'/cron/(.*)', Cron),
        (r'/error', Error),
        ]

application = webapp.WSGIApplication(urls, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

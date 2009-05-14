from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from apps.home import MainPage
from apps.twitter import Twitter
from apps.cron import Cron

urls = [
        (r'/', MainPage),
        (r'/twitter', Twitter),
        (r'/twitter/(.*)', Twitter),
        (r'/cron/(.*)', Cron),
        ]

application = webapp.WSGIApplication(urls, debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()

from google.appengine.api import users
from google.appengine.ext import webapp

from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import login_required

import os


class MainPage(webapp.RequestHandler):
    
    @login_required
    def get(self):
        print type(self)
        write = self.response.out.write
        
        user = users.get_current_user();
        path = os.path.join(os.path.dirname(__file__), '../templates/index.html')
        write(template.render(path, {'user':user,}))

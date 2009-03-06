# -*- coding: utf-8 -*-
from google.appengine.api import users
from gdata.alt.appengine import TokenCollection
from ragendja.template import render_to_response
from django.contrib.auth.decorators import login_required
import pickle
import settings

@login_required
def index(request):
    import gdata.service
    import gdata.alt.appengine
    import gdata.auth
    client = gdata.service.GDataService()
    gdata.alt.appengine.run_on_appengine(client)
    client.current_token = gdata.alt.appengine.load_auth_tokens()[settings.GOOGLE_BLOGSPOT_URL]
    token = gdata.alt.appengine.load_auth_tokens()[settings.GOOGLE_BLOGSPOT_URL]

    if token:
        feed = client.Get(settings.GOOGLE_BLOGSPOT_URL + 'default/blogs')
        data = {
            'token':token,
            'feed':feed,
            }
    else:
        data = {'error':'没有取得Blogspot的授权。'}
    return render_to_response(request, 'blogsearch/main.html', data = data)

def getToken():
    token = TokenCollection.all().filter('user =', users.get_current_user()).get()
    if token:
        return pickle.loads(token.pickled_tokens)
    else:
        return None

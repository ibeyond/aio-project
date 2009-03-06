# -*- coding: utf-8 -*-
from django.views.generic.list_detail import object_list
from django.http import HttpResponseRedirect, HttpResponse
from ragendja.template import render_to_response
from gdata.alt.appengine import TokenCollection
from django.contrib.auth.decorators import login_required
from google.appengine.api import users
import pickle
import atom.url
import home
import settings

def index(request):
    return render_to_response(request, 'main.html')

@login_required
def setting(request):
    if users.get_current_user() is None:
        return HttpResponseRedirect(users.create_login_url(request.get_full_path()))
    scheme = 'http'
    if request.is_secure():
        scheme = 'https'
    next_url = atom.url.Url(scheme, request.get_host(), path="/home/retrieve_token/")
    url = home.getAuthUrl(settings.GOOGLE_BLOGSPOT_URL, next_url)
    return render_to_response(request, 'home/setting.html', data={'url':url})

@login_required
def token_list(request):   
    if str(users.get_current_user().email()) != settings.SUPER_USER:
        return render_to_response(request, 'main.html', data={'error':'你不是超级用户'})
    token_list = [{'user':token.user,'token':pickle.loads(token.pickled_tokens)} for token in TokenCollection.all()]
    return object_list(request, token_list, paginate_by=10, template_name='home/token_list.html')

@login_required
def retrieve_token(request):
    import gdata.service
    import gdata.alt.appengine
    import gdata.auth
    client = gdata.service.GDataService()
    gdata.alt.appengine.run_on_appengine(client)
    scheme = 'http'
    if request.is_secure():
        scheme = 'https'
    auth_token = gdata.auth.extract_auth_sub_token_from_url(scheme +'://' + request.get_host() + request.get_full_path())
    if auth_token:
        session_token = client.upgrade_to_session_token(auth_token)
    if users.get_current_user() and session_token:
        client.token_store.add_token(session_token)
    return HttpResponseRedirect('/home/setting/')

# -*- coding: utf-8 -*-
def getAuthUrl(service_url, next_url):
    import gdata.service
    import gdata.alt.appengine
    client = gdata.service.GDataService()
    gdata.alt.appengine.run_on_appengine(client)
    #暂时不采用SSL
    return client.GenerateAuthSubURL(next_url, (service_url,), secure=True, session=True)
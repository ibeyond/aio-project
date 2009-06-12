# -*- coding: utf-8 -*-

'''
Created on Jun 12, 2009

@author: SongQingJie
'''

def get_request_token_info(__service, __meth='GET', **extra_params):
    return get_data_from_signed_url(__service.request_token_url,__service, __meth, **extra_params)

def get_data_from_signed_url(__url, __service, __meth='GET', **extra_params):
    if __meth == 'GET':
        result = urlfetch.fetch(get_signed_url(__url, __service, __meth, **extra_params))
        return result.content
    if __service.oauth_token is not None:
        methods ={'POST':urlfetch.POST, 'PUT':urlfetch.PUT, 'DELETE':urlfetch.DELETE}
        headers = get_auth_headers(__url, __service, __meth, **extra_params)
        if __service.service_name == 'twitter':
            return urlfetch.fetch(url=__url,payload=urlencode(extra_params),method=methods[__meth], headers=headers).content
        if __service.realm == 'https://www.blogger.com/feeds/':
            headers = get_auth_headers(__url, __service, __meth)
            headers['Content-Type'] = 'application/atom+xml'
            headers['GData-Version'] = '2'
            result = urlfetch.fetch(url=__url,payload=extra_params['body'],method=methods[__meth], headers=headers)
            return result.content
    
def get_signed_url(__url, __service, __meth='GET', **extra_params):
    kwargs = {
        'oauth_consumer_key': __service.consumer_key,
        'oauth_signature_method': 'HMAC-SHA1',
        'oauth_version': '1.0',
        'oauth_timestamp': int(time()),
        'oauth_nonce': getrandbits(64),
        }
    kwargs.update(extra_params)
    key = '%s&' % encode(__service.consumer_secret)
    if __service.oauth_token is not None:
        kwargs['oauth_token'] = __service.oauth_token
        key += encode(__service.oauth_token_secret)
    elif __service.req_oauth_token is not None:
        kwargs['oauth_token'] = __service.req_oauth_token
        key += encode(__service.req_oauth_token_secret)
    
           
    message = '&'.join(map(encode, [
        __meth.upper(), __url, '&'.join(
            '%s=%s' % (encode(k), encode(kwargs[k])) for k in sorted(kwargs)
            )
        ]))
    kwargs['oauth_signature'] = hmac(
        key, message, sha1
        ).digest().encode('base64')[:-1]
    return '%s?%s' % (__url, urlencode(kwargs))

def get_auth_headers(__url,__service, __meth='GET', **extra_params):
    message_info = get_signed_url(__url, __service, __meth,  **extra_params)
    header_name = ['oauth_version', 'oauth_token', 'oauth_nonce', 'oauth_timestamp', 'oauth_signature', 'oauth_consumer_key', 'oauth_signature_method',]
    auth = ', '.join(['%s="%s"' % (param.split('=')[0], param.split('=')[1]) for param in message_info.split('?')[1].split('&') if param.split('=')[0] in header_name])
    return {'Authorization':'OAuth realm="%s", %s' % (__service.realm, auth)}


def encode(text):
    return urlquote(str(text), '')
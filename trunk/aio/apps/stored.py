# -*- coding: utf-8 -*-

from google.appengine.ext import db
class AIOBase(db.Model):
    user = db.UserProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class Counter(AIOBase):
    name = db.StringProperty()
    value = db.IntegerProperty()
    
class OAuthService(AIOBase):
    realm = db.StringProperty(required=True)
    service_name = db.StringProperty(required=True)
    consumer_key = db.StringProperty(required=True)
    consumer_secret = db.StringProperty(required=True)
    request_token_url = db.LinkProperty(required=True)
    access_token_url = db.LinkProperty(required=True)
    user_auth_url = db.LinkProperty(required=True)
    req_oauth_token = db.StringProperty()
    req_oauth_token_secret = db.StringProperty()
    oauth_token = db.StringProperty()
    oauth_token_secret = db.StringProperty()
    user_id = db.StringProperty()


class TwitterUser(AIOBase):
    user_id = db.StringProperty()
    name = db.StringProperty()
    screen_name = db.StringProperty()
    location = db.StringProperty()
    description = db.StringProperty()
    profile_image_url = db.StringProperty()
    url = db.StringProperty()
    protected = db.BooleanProperty()
    followers_count = db.IntegerProperty()
    friends_count = db.IntegerProperty()
    created_at = db.StringProperty()
    favourites_count = db.IntegerProperty()
    utc_offset = db.IntegerProperty()
    time_zone = db.StringProperty()
    statuses_count = db.IntegerProperty()
    notifications = db.BooleanProperty()
    following = db.BooleanProperty()

class TwitterStatus(AIOBase):
    status_id = db.IntegerProperty()
    text = db.StringProperty(multiline=True)
    source = db.StringProperty()
    truncated = db.BooleanProperty()
    in_reply_to_status_id = db.IntegerProperty()
    in_reply_to_user_id = db.IntegerProperty()
    favorited = db.BooleanProperty()
    in_reply_to_screen_name = db.StringProperty()
    twitter_user = db.ReferenceProperty(TwitterUser)
    twitter_user_id = db.IntegerProperty()
    published_at = db.DateTimeProperty()
    created_at = db.StringProperty()
    
class BlogSite(AIOBase):
    link = db.StringProperty()
    category = db.StringListProperty()
    blog_id = db.StringProperty()
    title = db.StringProperty()
    summary = db.StringProperty()

class TwitterBlog(AIOBase):
    blog_id = db.StringProperty()
    category = db.StringProperty()
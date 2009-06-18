# -*- coding: utf-8 -*-

from google.appengine.ext import db


class AIOBase(db.Model):
    user = db.UserProperty(required=True)
    created = db.DateTimeProperty(auto_now_add=True)
    updated = db.DateTimeProperty(auto_now=True)

class Account(AIOBase):
    email = db.StringProperty()

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
    user_id = db.IntegerProperty()
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
    profile_sidebar_fill_color = db.StringProperty()
    profile_text_color = db.StringProperty()
    profile_background_color = db.StringProperty()
    profile_link_color = db.StringProperty()
    profile_background_image_url = db.StringProperty()
    profile_background_tile = db.BooleanProperty()
    profile_sidebar_border_color = db.StringProperty()

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

class TwitterFriend(AIOBase):
    user_id = db.IntegerProperty()
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
    profile_sidebar_fill_color = db.StringProperty()
    profile_text_color = db.StringProperty()
    profile_background_color = db.StringProperty()
    profile_link_color = db.StringProperty()
    profile_background_image_url = db.StringProperty()
    profile_background_tile = db.BooleanProperty()
    profile_sidebar_border_color = db.StringProperty()

class TwitterFriendStatus(AIOBase):
    status_id = db.IntegerProperty()
    text = db.StringProperty(multiline=True)
    source = db.StringProperty()
    truncated = db.BooleanProperty()
    in_reply_to_status_id = db.IntegerProperty()
    in_reply_to_user_id = db.IntegerProperty()
    favorited = db.BooleanProperty()
    in_reply_to_screen_name = db.StringProperty()
    twitter_user = db.ReferenceProperty(TwitterFriend)
    twitter_user_id = db.IntegerProperty()
    published_at = db.DateTimeProperty()
    created_at = db.StringProperty()
    
class BlogSite(AIOBase):
    link = db.StringProperty()
    category = db.StringListProperty()
    blog_id = db.StringProperty()
    title = db.StringProperty()
    summary = db.StringProperty()
    total_results = db.IntegerProperty()
    published = db.StringProperty()
    published_at = db.DateTimeProperty()
    updated_rss = db.StringProperty()
    updated_rss_at = db.DateTimeProperty()

class TwitterBlog(AIOBase):
    blog_id = db.StringProperty()
    category = db.StringProperty()

class Keyword(AIOBase):
    keyword_name = db.StringProperty()
    keyword_value = db.StringProperty()
    keyword_category = db.StringProperty()
    
class BlogPost(AIOBase):
    blog_id = db.StringProperty()
    post_id = db.StringProperty()
    category = db.StringListProperty()
    title = db.StringProperty()
    link = db.LinkProperty()
    published = db.StringProperty()
    published_at = db.DateTimeProperty()
    updated_at = db.DateTimeProperty()
    updated_b = db.StringProperty()
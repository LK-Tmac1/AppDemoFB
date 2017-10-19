import facebook, time
from entity import Post, PageEntity, PostPublished
from utility import real_time_to_unix
from cache import CachedPost


class PagePostClient(object):
    def __init__(self):
        # the client for a page
        self.api = facebook.GraphAPI()
        self.page = PageEntity(page_id="Unknown", page_name="Unknown")
        # here the cache is per post level, i.e. for each type of post, there is a cache
        self.cacheP = CachedPost("published")
        self.cacheU = CachedPost("unpublished")
        self.cacheS = CachedPost("scheduled")

    def cache_remove_one_batch(self, post_id):
        self.cacheS.remove_one(post_id)
        self.cacheU.remove_one(post_id)
        self.cacheP.remove_one(post_id)

    def cache_remove_all_batch(self):
        self.cacheS.remove_all()
        self.cacheU.remove_all()
        self.cacheP.remove_all()

    def cache_expire_batch(self):
        self.cacheS.expire = True
        self.cacheU.expire = True
        self.cacheP.expire = True

    def get_cache(self, publish_status):
        # given a publish_status, return the corresponding data cached
        if publish_status == "published":
            return self.cacheP
        if publish_status == "scheduled":
            return self.cacheS
        if publish_status == "unpublished":
            return self.cacheU

    def list_post(self, publish_status):
        cache = self.get_cache(publish_status)
        if cache.is_expired():
            base_url = "me/promotable_posts?fields=%s&is_published=" % Post.get_target_fields(publish_status)
            base_url += "false" if publish_status != 'published' else "true"
            response = self.api.get_object(id=base_url)
            post_list = Post.parse_post_from_json(response.get('data'), publish_status=publish_status)
            cache.remove_all()
            cache.add_new(post_list)
            cache.expire = False
        return cache.get_all_data()

    def create_post(self, message, published_status, scheduled_time=None, post_id=None):
        parameters = {"message": message}
        if published_status == "published":
            parameters["published"] = True
        elif published_status == "scheduled":
            scheduled_publish_time = real_time_to_unix(scheduled_time)
            if type(scheduled_publish_time) is int and scheduled_publish_time - int(time.time()) >= 60:
                # need to ensure the scheduled_publish_time is a valid one: an int and at least 60 secs later
                parameters["scheduled_publish_time"] = scheduled_publish_time
        parent_object, connection_name = "me", "feed"
        if post_id:
            # if post id is provided, it is equivalent to update a given post
            parent_object, connection_name = post_id, ''
            if published_status == "published":
                # if it has been already published, need to pop published and scheduled_publish_time from parameters
                parameters.pop("published", None)
                parameters.pop("scheduled_publish_time", None)
        response = self.api.put_object(parent_object, connection_name, **parameters)
        if 'id' in response and 'error' not in response:
            # if the creation/updating succeeds, set all caches as expired and return True to caller
            self.cache_remove_all_batch()
            self.cache_expire_batch()
            return True
        # otherwise, return the response failure obtained from API call
        return response

    def update_token(self, access_token):
        self.api = facebook.GraphAPI(access_token)
        json_data = self.api.get_object("me")
        self.page = PageEntity(page_id=json_data['id'], page_name=json_data['name'])
        self.get_page_insights()
        self.cache_remove_all_batch()

    def get_target_post(self, post_id, publish_status):
        # no need to update the expiration status of the cache here as it is only one target post
        cache = self.get_cache(publish_status)
        target_post = cache.get_by_post_id(post_id)
        if target_post is None:
            base_url = "%s?fields=%s" % (post_id, Post.get_target_fields(publish_status))
            response = self.api.get_object(id=base_url)
            post_list = Post.parse_post_from_json([response], publish_status)
            target_post = post_list[0] if post_list else None
            cache.add_new(post_list)
        return target_post

    def delete_post(self, post_id):
        self.api.delete_object(post_id)
        # remove this post from cached data if any
        self.cache_remove_one_batch(post_id)
        return True

    def get_post_insights(self, post):
        # it must be a published post
        # insights data won't be cached as we might want to return the latest one
        base_url = "%s/insights/%s" % (post.page_post_id, PostPublished.insights_fields)
        response = self.api.get_object(id=base_url)
        post.parse_post_insight_from_json(response.get('data', []))
        return

    def get_post_insights_batch(self):
        post_list = self.list_post("published")
        for post in post_list:
            self.get_post_insights(post)
        return post_list

    def get_page_insights(self):
        base_url = "%s/insights/%s?period=week" % (self.page.page_id, PageEntity.insights_fields)
        response = self.api.get_object(id=base_url)
        self.page.parse_page_insights_from_json(response.get('data', []))
        return

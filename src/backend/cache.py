import time


class CachedPost(object):
    def __init__(self, name, threshold):
        # use dict to cache data to avoid calling API duplicated times
        self.cached_data = dict([])
        self.expire = True
        self.name = name
        self.last_update_time = time.time()
        self.threshold = threshold

    def is_expired(self):
        # if the flag is True, or there is no data cached, it expires so need to update by the client
        return self.expire is True or len(self.cached_data) == 0 or time.time() - self.last_update_time >= self.threshold

    def update_timer(self):
        self.last_update_time = time.time()

    def remove_all(self):
        self.cached_data.clear()

    def remove_one(self, key):
        return self.cached_data.pop(key, None)

    def add_new_post(self, post):
        self.cached_data[post.page_post_id] = post

    def add_new_post_list(self, post_list):
        for post in post_list:
            self.add_new_post(post)

    def get_all_data(self):
        return self.cached_data.values()

    def get_by_post_id(self, post_id):
        return self.cached_data.get(post_id)

    def __repr__(self):
        return "%s: %s data, expired=%s" % (self.name, len(self.cached_data), self.expire)

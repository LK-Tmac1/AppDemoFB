class CachedData(object):
    def __init__(self, name):
        self.cached_data = dict([])
        self.expire = True
        self.name = name

    def is_expired(self):
        # if the flag is True, or there is no data cached, it expires so need to update by the client
        return self.expire is True or len(self.cached_data) == 0

    def __repr__(self):
        return "%s: %s data, expired=%s" % (self.name, len(self.cached_data), self.expire)


class CachedPost(CachedData):
    def __init__(self, name):
        # use dict to cache data to avoid calling API duplicated times
        CachedData.__init__(self, name)

    def add_new(self, post_list):
        for post in post_list:
            self.cached_data[post.page_post_id] = post

    def get_all_data(self):
        return self.cached_data.values()

    def remove_one(self, post_id):
        self.cached_data.pop(post_id, None)

    def remove_all(self):
        self.cached_data.clear()

    def get_by_post_id(self, post_id):
        return self.cached_data.get(post_id)


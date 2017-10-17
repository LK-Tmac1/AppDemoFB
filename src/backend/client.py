import facebook, time
from entity import Post, PageEntity
from utility import real_time_to_unix


class PageClient(object):
    def __init__(self, access_token=None):
        # the client for a page
        self.api = facebook.GraphAPI(access_token)
        self.page = PageEntity(page_id="Unknown", page_name="Unknown")
        self.page_name = "Unknown"

    def list_post(self, publish_status):
        base_url = "me/promotable_posts?fields=%s&is_published=" % Post.get_target_fields(publish_status)
        base_url += "false" if publish_status != 'published' else "true"
        response = self.api.get_object(id=base_url)
        post_list = Post.parse_post_from_json(response.get('data'), publish_status=publish_status)
        return post_list

    def list_unpublished_posts(self):
        return self.list_post(publish_status="unpublished")

    def list_published_posts(self):
        return self.list_post(publish_status="published")

    def list_scheduled_posts(self):
        return self.list_post(publish_status="scheduled")

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
            # so it must be published already, need to pop published and scheduled_publish_time from parameters
            parent_object, connection_name = post_id, ''
            parameters.pop("published", None)
            parameters.pop("scheduled_publish_time", None)
        return self.api.put_object(parent_object, connection_name, **parameters)

    def update_token(self, access_token):
        self.api = facebook.GraphAPI(access_token)
        json_data = self.api.get_object("me")
        self.page = PageEntity(page_id=json_data['id'], page_name=json_data['name'])
        self.page_name = json_data['name']

    def get_posts_by_published_status(self, publish_status):
        if publish_status == 'unpublished':
            return self.list_unpublished_posts()
        elif publish_status == 'scheduled':
            return self.list_scheduled_posts()
        return self.list_published_posts()

    def get_target_post(self, post_id, publish_status):
        base_url = "%s?fields=%s" % (post_id, Post.get_target_fields(publish_status))
        response = self.api.get_object(id=base_url)
        post_list = Post.parse_post_from_json([response], publish_status)
        return post_list[0] if post_list else None

    def delete_post(self, post_id):
        self.api.delete_object(post_id)

import facebook, time
from entity import Post, PageEntity
from utility import real_time_to_unix


class PageClient(object):
    def __init__(self, access_token=None):
        # the client for a page
        self.api = facebook.GraphAPI(access_token)
        self.page = PageEntity(page_id="Unknown", page_name="Unknown")

    def list_post(self, is_published=None):
        base_url = "me/promotable_posts?fields=%s" % Post.target_fields
        if is_published is not None:
            base_url += "&is_published=%s" % is_published
        response = self.api.get_object(id=base_url)
        post_list = Post.parse_post_from_json(response.get('data'), is_published=is_published)
        return post_list

    def list_unpublished_posts(self):
        return self.list_post(is_published=False)

    def list_published_posts(self):
        return self.list_post(is_published=True)

    def create_post(self, message, published_status, scheduled_time=None, post_id=None):
        parameters = {"message": message, "published": True}
        if published_status != "published":
            parameters["published"] = False
        if published_status == "scheduled":
            scheduled_publish_time = parameters["scheduled_publish_time"] = real_time_to_unix(scheduled_time)
            if type(scheduled_publish_time) is not int or scheduled_publish_time - int(time.time()) < 60:
                # need to ensure the scheduled_publish_time is a valid one: an int and at least 60 secs later
                parameters.pop("scheduled_publish_time")
        parent_object, connection_name = "me", "feed"
        if post_id:
            # if post id is provided, it is equivalent to update a given post
            parent_object, connection_name = post_id, ''
        return self.api.put_object(parent_object, connection_name, **parameters)

    def update_token(self, access_token):
        self.api = facebook.GraphAPI(access_token)
        json_data = self.api.get_object("me")
        self.page = PageEntity(page_id=json_data['id'], page_name=json_data['name'])

    def get_posts_by_published_status(self, publish_status):
        if publish_status == 'published':
            post_list = self.list_published_posts()
        elif publish_status == 'unpublished' or publish_status == 'scheduled':
            post_list =self.list_unpublished_posts()
            scheduled, unscheduled = Post.split_unpublished_posts(post_list)
            post_list = scheduled if publish_status == 'scheduled' else unscheduled
        else:
            post_list = self.list_post()
        return post_list

    def get_target_post(self, post_id):
        base_url = "%s?fields=%s" % (post_id, Post.target_fields)
        response = self.api.get_object(id=base_url)
        post_list = Post.parse_post_from_json([response], None)
        return post_list[0] if post_list else None

    def delete_post(self, post_id):
        self.api.delete_object(post_id)


# client = PageClient("EAACEdEose0cBAGFZBpzULFHJQIFaJKHpyLgcNMPR0g5eTh1ugo5jpgQXCcTZCZASG5UrBIUm8zrh45cTmC614ig2397VWuOQhhf5BYojzvRKNpviK3pvUuMTWEBitkVEjZB0J7WzhkIgAZAVZADNzqKNtCuZCXMIKjmUB7sPeoeykSKfQjYjrh8M6hN3ZBkNgNIV4BE2kAfiIQZDZD")
# print client.create_post("Sample post 2", "scheduled", 1514156400)
# client.delete_post("130309607624409_131965767458793")


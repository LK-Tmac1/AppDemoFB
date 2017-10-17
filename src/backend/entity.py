import random
from utility import parse_str_date, unix_to_real_time


class PageEntity(object):
    def __init__(self, page_id, page_name):
        self.page_id = page_id
        self.page_name = page_name


class Post(object):
    target_fields = "created_time,updated_time,message,promotion_status,scheduled_publish_time,is_published"

    def __init__(self, page_post_id, created_time, message):
        self.page_post_id = page_post_id
        self.created_time = parse_str_date(created_time)
        self.message = message
        self.promotion_status = self.updated_time = self.publish_status = ""
        self.num_of_view = ""

    def change_publish_status(self, publish_status):
        self.publish_status = publish_status
        if self.publish_status.lower() == "published":
            self.num_of_view = random.randint(3, 40)

    @staticmethod
    def split_unpublished_posts(unpublished_posts):
        # Split unpublished posts into scheduled and unscheduled
        scheduled, unscheduled = list([]), list([])
        for post in unpublished_posts:
            if post.publish_status and post.publish_status[0] == 'S':
                scheduled.append(post)
            else:
                unscheduled.append(post)
        return scheduled, unscheduled

    @staticmethod
    def parse_post_from_json(json_data, is_published):
        def parse_published_status(post_published, scheduled_publish_time=None):
            # if post_published is specified as True or False (not None), possibly 3 types of status
            # 1. published, then yes 2. not published but scheduled 3. not published nor scheduled
            if post_published is True:
                return "Published"
            elif post_published is False:
                if scheduled_publish_time:
                    return "Scheduled on %s" % unix_to_real_time(int(scheduled_publish_time))
            return "Unpublished"

        post_list = list([])
        if json_data:
            for post_obj in json_data:
                if "message" in post_obj:
                    post = Post(page_post_id=post_obj['id'],
                                created_time=post_obj['created_time'],
                                message=post_obj['message'])
                    post.updated_time = post_obj.get("update_date", "")
                    post.promotion_status = str(post_obj.get("promotion_status", "")).title()
                    if is_published is None:
                        # list both published and unpublished/scheduled posts
                        if "is_published" in post_obj:
                            if str(post_obj["is_published"]).lower() == "true":
                                publish_status = "Published"
                            else:
                                publish_status = parse_published_status(False, post_obj.get('scheduled_publish_time'))
                        else:
                            publish_status = "Unknown"
                    else:
                        publish_status = parse_published_status(is_published, post_obj.get('scheduled_publish_time'))
                    post.change_publish_status(publish_status)
                    post_list.append(post)
        return post_list

    def __repr__(self):
        return "%s, %s, %s, %s" % (self.promotion_status, self.page_post_id, self.created_time, self.publish_status)

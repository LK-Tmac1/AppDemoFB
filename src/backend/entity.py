import random
from utility import parse_str_date, unix_to_real_time


class PageEntity(object):
    insights_fields = "page_impressions,page_impressions_paid,page_engaged_users," \
                           "page_video_views,page_video_views_paid,page_views_total"

    def __init__(self, page_id, page_name):
        self.page_id = page_id
        self.page_name = page_name
        self.page_impressions = -1
        self.page_impressions_paid = -1
        self.page_engaged_users = -1
        self.page_video_views = -1
        self.page_video_views_paid = -1
        self.page_views_total = -1

    def parse_page_insights_from_json(self, json_data):
        for obj in json_data:
            name = obj['name']
            values = obj['values']
            value = ""
            if type(values) is list and len(values) >= 2:
                # one unique one organic, get the average
                value = ((values[0]['value'] + values[1]['value'])/2)
            if name == "page_video_views_paid":
                self.page_video_views_paid = value
            elif name == "page_video_views":
                self.page_video_views = value
            elif name == "page_impressions":
                self.page_impressions = value
            elif name == "page_impressions_paid":
                self.page_impressions_paid = value
            elif name == "page_engaged_users":
                self.page_engaged_users = value
            elif name == "page_views_total":
                self.page_views_total = value


class Post(object):
    @staticmethod
    def get_target_fields(publish_status):
        base_field = "created_time,message,admin_creator"
        if publish_status == "published":
            base_field += ",promotion_status"
        elif publish_status == "scheduled":
            base_field += ",scheduled_publish_time"
        return base_field

    def __init__(self, page_post_id, created_time, message, admin_creator):
        self.page_post_id = page_post_id
        self.created_time = parse_str_date(created_time)
        self.message = message
        self.admin_creator = admin_creator

    @staticmethod
    def parse_post_from_json(json_data, publish_status):
        post_list = list([])
        if json_data:
            for post_obj in json_data:
                if "message" in post_obj:
                    page_post_id = post_obj['id']
                    created_time = post_obj['created_time']
                    message = post_obj['message']
                    admin_creator = post_obj['admin_creator']['name']
                    if publish_status == "published":
                        promotion_status = str(post_obj.get("promotion_status", "")).title()
                        post = PostPublished(page_post_id, created_time, message, promotion_status, admin_creator)
                    elif publish_status == "scheduled":
                        if "scheduled_publish_time" not in post_obj:
                            continue
                        scheduled_publish_time = post_obj['scheduled_publish_time']
                        scheduled_time = unix_to_real_time(int(scheduled_publish_time))
                        post = PostScheduled(page_post_id, created_time, message, scheduled_time, admin_creator)
                    else:
                        post = PostUnpublished(page_post_id, created_time, message, admin_creator)
                    post_list.append(post)
        return post_list


class PostPublished(Post):
    insights_fields = "post_impressions_fan_paid,post_impressions_fan," \
                      "post_impressions_paid,post_impressions,post_consumptions," \
                      "post_engaged_users,post_negative_feedback,post_fan_reach,post_engaged_fan"

    def __init__(self, page_post_id, created_time, message, promotion_status, admin_creator):
        Post.__init__(self, page_post_id, created_time, message, admin_creator)
        self.promotion_status = promotion_status
        self.post_impressions_fan_paid = self.post_impressions_fan = -1
        self.post_impressions_paid = self.post_impressions = -1
        self.post_consumptions = -1
        self.post_engaged_users = -1
        self.post_negative_feedback = -1
        self.post_fan_reach = -1
        self.post_engaged_fan = -1

    def parse_post_insight_from_json(self, json_data):
        for obj in json_data:
            name = obj['name']
            values = obj['values']
            value = values[0]['value'] if type(values) is list else ""
            if name == "post_impressions_fan_paid":
                self.post_impressions_fan_paid = value
            elif name == "post_impressions_fan":
                self.post_impressions_fan = value
            elif name == "post_impressions_paid":
                self.post_impressions_paid = value
            elif name == "post_impressions":
                self.post_impressions = value
            elif name == "post_consumptions":
                self.post_consumptions = value
            elif name == "post_engaged_users":
                self.post_engaged_users = value
            elif name == "post_negative_feedback":
                self.post_negative_feedback = value
            elif name == "post_fan_reach":
                self.post_fan_reach = value
            elif name == "post_engaged_fan":
                self.post_engaged_fan = value


class PostUnpublished(Post):
    def __init__(self, page_post_id, created_time, message, admin_creator):
        Post.__init__(self, page_post_id, created_time, message, admin_creator)


class PostScheduled(Post):
    def __init__(self, page_post_id, created_time, message, scheduled_time, admin_creator):
        Post.__init__(self, page_post_id, created_time, message, admin_creator)
        self.scheduled_time = scheduled_time

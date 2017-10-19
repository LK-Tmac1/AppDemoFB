import xlsxwriter
from utility import parse_str_date, unix_to_real_time, prepare_parent_dir


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
            setattr(self, name, value)


class Post(object):
    @staticmethod
    def get_target_fields(publish_status):
        base_field = "created_time,message,admin_creator"
        if publish_status == "published":
            base_field += ",promotion_status"
        elif publish_status == "scheduled":
            base_field += ",scheduled_publish_time"
        return base_field

    def __init__(self, page_post_id, created_time, message, admin_creator, publish_status):
        self.page_post_id = page_post_id
        self.created_time = parse_str_date(created_time)
        self.message = message
        self.admin_creator = admin_creator
        self.published_status = publish_status

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
    insights_fields_list = insights_fields.split(",")
    excel_header_list = ["promotion_status", "created_time", "message", "admin_creator"] + insights_fields_list

    def __init__(self, page_post_id, created_time, message, promotion_status, admin_creator):
        Post.__init__(self, page_post_id, created_time, message, admin_creator, "published")
        self.promotion_status = promotion_status

    def parse_post_insight_from_json(self, json_data):
        for obj in json_data:
            name = obj['name']
            values = obj['values']
            value = values[0]['value'] if type(values) is list else ""
            setattr(self, name, value)

    def to_excel_data(self):
        data = []
        for field in PostPublished.excel_header_list:
            value = self.__getattribute__(field)
            data.append(value)
        return data

    @staticmethod
    def save_to_excel_file(excel_output_path, post_list):
        prepare_parent_dir(excel_output_path)
        wbk = xlsxwriter.Workbook(filename=excel_output_path)
        sheet = wbk.add_worksheet('sheet1')
        for i in xrange(len(PostPublished.excel_header_list)):
            sheet.write(0, i, PostPublished.excel_header_list[i])
        row = 1
        for post in post_list:
            if post:
                col = 0
                for d in post.to_excel_data():
                    sheet.write(row, col, d)
                    col += 1
                row += 1
        wbk.close()
        return True


class PostUnpublished(Post):
    def __init__(self, page_post_id, created_time, message, admin_creator):
        Post.__init__(self, page_post_id, created_time, message, admin_creator, "unpublished")


class PostScheduled(Post):
    def __init__(self, page_post_id, created_time, message, scheduled_time, admin_creator):
        Post.__init__(self, page_post_id, created_time, message, admin_creator, "scheduled")
        self.scheduled_time = scheduled_time

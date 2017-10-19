from datetime import datetime
from dateutil import tz
import time, os, requests


def get_current_datetime():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %I:%M:%S %p")


def prepare_parent_dir(file_path):
    if not file_path or os.path.exists(file_path.strip()):
        parent_dir = file_path[0:file_path.rfind(os.sep)]
        os.makedirs(parent_dir)


def get_min_schedule_date(min_offset=5):
    min_schedule_date_time = int(time.time()) + min_offset * 60
    return datetime.fromtimestamp(min_schedule_date_time).strftime('%Y-%m-%dT%H:%M')


def parse_str_date(str_date):
    if not str_date:
        return ""
    try:
        from_zone = tz.tzutc()
        to_zone = tz.tzlocal()
        str_date = str_date.split("+")
        utc = datetime.strptime(str_date[0], '%Y-%m-%dT%H:%M:%S')
        utc = utc.replace(tzinfo=from_zone)
        local_time = utc.astimezone(to_zone)
        date_str = '%s-%s-%s %s:%s' % (local_time.year, local_time.month, local_time.day,
                                       local_time.hour, local_time.minute)
        return datetime.strptime(date_str, '%Y-%m-%d %H:%M').strftime('%Y-%m-%d %I:%M %p')
    except Exception:
        return str_date


def unix_to_real_time(unix_int):
    try:
        return datetime.fromtimestamp(unix_int).strftime('%Y-%m-%d %I:%M %p')
    except Exception:
        return ""


def real_time_to_unix(date_time_str):
    date_time_str = date_time_str.replace("T", " ")
    return int(datetime.strptime(date_time_str, '%Y-%m-%d %H:%M').strftime("%s"))


class Email(object):
    def __init__(self, email_api_key, email_to, subject):
        self._from = "FB Page Admin <postmaster@sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org>"
        self._to = email_to
        self._post_url = "https://api.mailgun.net/v3/sandbox37699e306f69436d8f89f81915ad9f0a.mailgun.org/messages"
        self._api_key = email_api_key
        self.subject = subject
        self.text_list = list([])
        self.attachment_list = list([])

    def add_text(self, text, append=True):
        if append:
            self.text_list.append(text)
        else:
            self.text_list = list([text])

    def add_attachment(self, file_path):
        self.attachment_list.append(("attachment", open(file_path)))

    def send(self):
        data = {"from": self._from, "to": self._to, "subject": self.subject, "text": "\n".join(self.text_list)}
        auth = ("api", self._api_key)
        result = requests.post(self._post_url, auth=auth, data=data,files=self.attachment_list)
        return result.status_code == 200

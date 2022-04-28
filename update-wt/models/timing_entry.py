from dateutil.parser import parse

import helpers


class TimingEntry:
    def __init__(self, obj):
        self.timing_object = obj
        try:
            self.activity_title = obj["activityTitle"]
        except KeyError:
            self.activity_title = str()
        self.application = obj["application"]
        self.duration = obj["duration"]
        self.id = obj["id"]
        try:
            self.path = obj["path"]
        except KeyError:
            self.path = str()
        self.project = obj["project"]
        self.start_date = obj["startDate"]
        self.type = None
        self.category = None

    def _prepare_times(self):
        start_date = parse(self.start_date, fuzzy_with_tokens=True)
        self.start_time = start_date[0].timestamp()
        self.end_time = self.start_time + self.duration
        return

    def _deduce_language(self):
        self.language = helpers.deduce_language(self.timing_object)

    def _deduce_type(self):
        entity = self.path
        if not entity:
            return
        if entity.startswith("http"):
            self.type = "domain"
        elif entity.startswith("file:"):
            self.type = "file"

    def _deduce_category(self):
        app = self.application
        at = self.activity_title
        path = self.path
        browsers = ['Safari', 'Google Chrome', 'Firefox Developer Edition']
        if app in browsers:
            if ' - WordPress' in at:
                self.category = 'designing'
                self.language = 'WordPress'
            elif 'Oxygen Visual Editor' in at:
                self.category = 'designing'
                self.language = 'WordPress'
                self.application = 'Oxygen Builder'
            elif 'cluster-60d4b8a9c1ac1b3b3c59885a.closte.com' in path:
                self.category = 'coding'
                self.language = 'SQL'
            elif 'wp-admin' in path:
                self.category = 'designing'
                self.language = 'WordPress'
            else:
                self.category = 'browsing'

    def to_wakatime(self):
        self._prepare_times()
        self._deduce_language()
        self._deduce_type()
        self._deduce_category()
        w_obj = {
            "external_id": self.id,
            "entity": self.path,
            "type": self.type,
            "category": self.category,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "project": self.project,
            "language": self.language,
        }

        wakatime_object = {k: v for k, v in w_obj.items() if v is not None}

        return wakatime_object

    def post_to_wakatime(self):
        return self

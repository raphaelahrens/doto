import json
import datetime
import pytz
import subprocess
import config


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    keys = list(value for value in enums.iterkeys())
    ident = enums.copy()
    enums['keys'] = keys
    enums['ident'] = ident.get
    return type('Enum', (), enums)

STATE = enum("pending", "started", "blocked", "paused", "completed", "deleted")
DIFFICULTY = enum("unknown", "simple", "easy", "medium", "hard")


def str_from_time_span(t_span):
    def one_or_more(t, single_str, multiple_str):
        return single_str % t if t == 1 else multiple_str % t
    if t_span.days < 0:
        raise
    if t_span.days > 0:
        return one_or_more(t_span.days, "%d day", "%d days")
    if t_span.seconds > 3600:
        return one_or_more(t_span.seconds // 3600, "%d hour", "%d hours")
    if t_span.seconds > 60:
        return one_or_more(t_span.seconds // 60, "%d minute", "%d minutes")
    return one_or_more(t_span.seconds, "%d second", "%d seconds")


class JSONSerialize(object):
    ser_classes = {}

    module_id = "__module__"
    class_id = "__class__"
    member_id = "__members__"

    @classmethod
    def add_class(cls):
        JSONSerialize.ser_classes[cls.__name__] = cls

    @classmethod
    def create_dict(cls, members):
        return {JSONSerialize.module_id: cls.__module__,
                JSONSerialize.class_id: cls.__name__,
                JSONSerialize.member_id: members}

    @classmethod
    def new_from_json(cls, d):
        tmp = JSONSerialize()
        tmp.__dict__ = d
        tmp.__class__ = cls
        return tmp

    def json_serialize(self):
        return self.__class__.create_dict(self.__dict__)


class Date(datetime.datetime, JSONSerialize):

    utc_id = "utc"
    local_tz = pytz.timezone(config.local_tz)

    def get_local(self):
        return self.astimezone(Date.local_tz)

    def json_serialize(self):
        return Date.create_dict({Date.utc_id: (self.year,
                                               self.month,
                                               self.day,
                                               self.hour,
                                               self.minute,
                                               self.second,
                                               self.microsecond)
                                 })

    @classmethod
    def new_from_json(cls, d):
        year, month, day, hour, minute, second, ms = d[Date.utc_id]
        return Date(year, month, day, hour, minute, second, ms, pytz.utc)
Date.add_class()


class TimeSpan(JSONSerialize):
    def __init__(self, start=None, end=None):
        self._start = None
        self._end = None
        self.start = start
        self.end = end

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, start):
        if start is not None:
            assert isinstance(start, Date), "The argument start is of type %r and not task.Date." % type(start)
            assert self._end is None or self._end >= start, "The start date must be older then the start date."
        self._start = start

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, end):
        if end is not None:
            assert end is None or isinstance(end, Date), "The argument end is of type %r and not task.Date." % type(end)
            assert self._start is None or self._start <= end, "The end date must be newer then the start date."
        self._end = end

    def time_span(self):
        return self._end - self._start

    def time_left_str(self):
        return str_from_time_span(self.time_span)
TimeSpan.add_class()


class EncodeError(Exception):
    pass


class Task(JSONSerialize):
    """
    Super class of all tasks
    """
    def __init__(self, title, description, created=Date.now(), started=None, due=None,
                 difficulty=DIFFICULTY.unknown, state=STATE.pending):
        """
        """
        self.title = unicode(title)
        self.description = unicode(description)
        self.state = state
        self.difficulty = difficulty
        self.due = due
        self.category = None
        self.source = None

        self.schedule = TimeSpan()

        self.created = created
        self.started = started
Task.add_class()


class TaskEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, JSONSerialize):
            return o.json_serialize()


class TaskDecoder(json.JSONDecoder):
    def default(self, o):
        return json.JSONEncoder.default(self, o)


class TWTask(Task):
    def __init__(self, task_dict):
        def get_attr(string, default):
            if str in task_dict:
                return task_dict
            else:
                return default

        def get_time(s, d):
            return datetime.datetime.strptime(d[s], "%Y%m%dT%H%M%SZ") if s in d else None

        _description = "description"
        Task.__init__(self, task_dict[_description][0:10], task_dict[_description],
                      created=get_time("entry", task_dict),
                      due=get_time("due", task_dict),
                      started=get_time("start", task_dict)
                      )
        if "depends" in task_dict:
            self.depends = task_dict["depends"].split(",")
        else:
            self.depends = []

        self._id = task_dict["id"]
        self.uuid = task_dict["uuid"]
        self.status = STATE.ident(task_dict["status"])
        self.urgency = task_dict["urgency"]

        self.end = get_attr("end", None)
        self.recur = get_attr("recur", None)
        self.tags = get_attr("tags", None)
        self.modified = get_attr("modified", None)
        self.project = get_attr("project", None)

        self.data = task_dict

    def __str__(self):
        return unicode("uuid: %s\n Name: %s \n(%s)\n\n %s" % (self.uuid, self.description, self.status, self.data))

    def __repr__(self):
        return "(%s, %s)" % (self.uuid, self.description)


class TaskwarrioirStore(object):
    def __init__(self):
        output = subprocess.check_output(["task", "export"])
        items = map(TWTask, json.loads("[" + output + "]"))
        self.index = dict((x.uuid, x) for x in items)
        self.pending = [x for x in items if x.status == STATE.pending]

    def get_tasks(self):
        return self.pending

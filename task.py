import datetime
import pytz
import subprocess
import config

from serializer import JSONSerialize
from state import State


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    keys = list(value for value in enums.iterkeys())
    ident = enums.copy()
    enums['keys'] = keys
    enums['ident'] = ident.get
    return type('Enum', (), enums)

DIFFICULTY = enum("unknown", "simple", "easy", "medium", "hard")


def _add_new_state(d, key, name=None):
    state = State(key, name)
    print state
    d[key] = state
    return state


class TaskStateHolder(JSONSerialize):
    states = {}
    pending = _add_new_state(states, "pending")
    started = _add_new_state(states, "started")
    completed = _add_new_state(states, "completed")
    blocked = _add_new_state(states, "blocked")
    interrupted = _add_new_state(states, "interrupted")
    pending.set_neighbor(started, "start")
    started.set_neighbor(completed, "complete")
    started.set_neighbor(blocked, "block")
    started.set_neighbor(interrupted, "interrupt")
    blocked.set_neighbor(started, "unblock")
    interrupted.set_neighbor(started, "restart")

    def __init__(self, state=pending):
        self._state = state

    def next_state(self, action):
        self._state = self._state.next_state(action)

    def get_actions(self):
        return self._state.get_neighbors()

    def json_serialize(self):
        return TaskStateHolder.create_dict({"state": self._state.key})

    def __eq__(self, obj):
        return self._state.key == obj._state.key

    @classmethod
    def from_json(cls, d):
        return TaskStateHolder(state=TaskStateHolder.states[d["state"]])


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


class Date(JSONSerialize):
    utc_id = "utc"
    local_tz = pytz.timezone(config.local_tz)

    def __init__(self, date):
        self._date = date
        if self._date.tzinfo:
            self._date = self._date.astimezone(pytz.utc)
        else:
            raise AttributeError("The given date had no timezone data")

    def get_local(self):
        return self._date.astimezone(Date.local_tz)

    def json_serialize(self):
        return Date.create_dict({Date.utc_id: (self._date.year, self._date.month,
                                               self._date.day, self._date.hour,
                                               self._date.minute, self._date.second,
                                               self._date.microsecond)
                                 })

    def __lt__(self, o):
        return self._date <= Date._is_date(o)

    def __le__(self, o):
        return self._date <= Date._is_date(o)

    def __eq__(self, o):
        return self._date == Date._is_date(o)

    def __ge__(self, o):
        return self._date >= Date._is_date(o)

    def __gt__(self, o):
        return self._date > Date._is_date(o)

    def __sub__(self, o):
        return self._date - Date._is_date(o)

    def __add__(self, o):
        return self._date + Date._is_date(o)

    def local_str(self):
        return self._date.strftime(config.date_str)

    @classmethod
    def from_json(cls, d):
        year, month, day, hour, minute, second, ms = d[Date.utc_id]
        date = datetime.datetime(year, month, day, hour, minute, second, ms, pytz.utc)
        return Date(date)

    @classmethod
    def local(cls, year, month, day, hour=0, minute=0, second=0, microsecond=0):
        return Date(datetime.datetime(year, month, day, hour, minute, second, microsecond, tzinfo=Date.local_tz))

    @classmethod
    def now(cls, tz=local_tz):
        return Date(datetime.datetime.now(tz))

    def get_date(self):
        return self._date

    @staticmethod
    def _is_date(o):
        if isinstance(o, Date):
            return o._date
        return o


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

    def __eq__(self, obj):
        return isinstance(obj, TimeSpan) and self.end == obj.end and self.start == obj.start


class Task(JSONSerialize):
    """
    Super class of all tasks
    """
    def __init__(self, title, description, created=Date.now(), started=None, due=None,
                 difficulty=DIFFICULTY.unknown, state=TaskStateHolder()):
        """
        """
        self.title = unicode(title)
        self.description = unicode(description)
        self.state = TaskStateHolder()
        self.difficulty = difficulty
        self.due = due
        self.category = None
        self.source = None

        self.schedule = TimeSpan()

        self.created = created
        self.started = started

    def __eq__(self, obj):
        return (isinstance(obj, Task) and self.title == obj.title and self.description == obj.description and
                self.state == obj.state and self.difficulty == obj.difficulty and
                self.due == obj.due and self.category == obj.category and
                self.source == obj.source and self.schedule == obj.schedule and
                self.created == obj.created and self.started == obj.started)


class TWTask(Task):
    def __init__(self, task_dict):
        def get_attr(string, default):
            if str in task_dict:
                return task_dict
            else:
                return default

        def get_time(s, d):
            return Date(datetime.datetime.strptime(d[s], "%Y%m%dT%H%M%SZ")) if s in d else None

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
        self.status = TaskStateHolder()
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
        import json
        output = subprocess.check_output(["task", "export"])
        items = map(TWTask, json.loads("[" + output + "]"))
        self.index = dict((x.uuid, x) for x in items)
        self.pending = [x for x in items if x.status == "pending"]

    def get_tasks(self):
        return self.pending

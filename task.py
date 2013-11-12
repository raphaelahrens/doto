import json
import datetime
import subprocess


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


class Schedule:
    def __init__(self, start=None, end=None):
        self.__start = start
        self.__end = end

    @property
    def start(self):
        return self.__start

    @start.setter
    def start(self, value):
        self.__start = value

    @property
    def end(self):
        return self.__end

    @end.setter
    def end(self, value):
        self.__end = value

    def time_span(self):
        return self.__end - self.__start

    def time_left_str(self):
        return str_from_time_span(self.time_span)


class EncodeError(Exception):
    pass


class Task:
    """
    Super class of all tasks
    """
    def __init__(self, title, description, created=datetime.datetime.now(), started=None, due=None,
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

        self.schedule = Schedule()

        self.created = created
        self.started = started


class TaskEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Task):
            return {Task.__name__: o.__dict__}
        if isinstance(o, datetime.datetime):
            return {datetime.datetime.__name__: (o.year, o.month, o.day, o.hour, o.minute, o.second, o.microsecond)}
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


class TaskwarrioirStore:
    def __init__(self):
        output = subprocess.check_output(["task", "export"])
        items = map(TWTask, json.loads("[" + output + "]"))
        self.index = dict((x.uuid, x) for x in items)
        self.pending = [x for x in items if x.status == STATE.pending]

    def get_tasks(self):
        return self.pending

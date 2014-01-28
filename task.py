"""
This module implements the all base classes for a task of the Done!Tools.

The task module implements all basic classes for the Done!Tools project.
It's a base for all future plug-ins.

"""

import datetime
import pytz
import subprocess
import config
import sqlite3

import serializer
import statemachine


def create_difficulties(**difficulties):
    keys = []
    names = {}
    local_names = {}
    for name, (d_id, local) in difficulties.iteritems():
        names[name] = d_id
        local_names[d_id] = local
        keys.append(d_id)
    keys.sort()
    names["keys"] = keys
    names["local_names"] = local_names
    return type("Difficulty", (), names)


DIFFICULTY = create_difficulties(unknown=(0, "not set"),
                                 simple=(1, "simple"),
                                 easy=(2, "easy"),
                                 medium=(3, "medium"),
                                 hard=(4, "hard")
                                 )


def _add_new_state(states, key, name=None):
    """
    Add a new state to the dictionary and retrun the state.

    @param dir the dictionary to which the state will be added.
    @param key the key for the state
    @param name the name of the state

    @return the new state

    """
    state = statemachine.State(key, name)
    states[key] = state
    return state


class StateHolder(serializer.JSONSerialize):

    """
    This class is used to manage the state of a Task object.

    The StateHolder class holds the current state of the task and supports
    methods to manipulate the state of the task.

    Supported states are pending, started, completed, blocked, interrupted.

    """

    states = {}
    completed = statemachine.FinalState(states, "completed")
    states[completed.key] = completed
    pending = _add_new_state(states, "pending")
    started = _add_new_state(states, "started")
    blocked = _add_new_state(states, "blocked")
    interrupted = _add_new_state(states, "interrupted")
    pending.add_neighbor(started, "start")
    started.add_neighbor(completed, "complete")
    started.add_neighbor(blocked, "block")
    started.add_neighbor(interrupted, "interrupt")
    blocked.add_neighbor(started, "unblock")
    interrupted.add_neighbor(started, "restart")

    def __init__(self, state=pending):
        self._state = state

    @property
    def state(self):
        """ Return the current state."""
        return self._state

    def next_state(self, action):
        """Set the next state according to the given action."""
        self._state = self._state.next_state(action)

    def get_actions(self):
        """
        Get all possible action from the current state.

        @return a list of the action for the current state.

        """
        return self._state.get_actions()

    def json_serialize(self):
        """
        The method returns a dictionary which can be serialized into JSON.

        The dictionary returned by the message has the following form:
            {class, module, member1, member2, ...}
        A subclass is free to overwrite this method to create a better
        JSON representation.

        @return the dictionary created

        """
        return StateHolder.create_dict({"state": self._state.key})

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return self._state.key

    def __eq__(self, obj):
        if isinstance(obj, StateHolder):
            return self._state.key == obj.state.key
        return self._state.key == obj

    @classmethod
    def from_json(cls, d):
        """
        Use the dictionary d and creates a new object of this class.

        @param d the dictionary which was created from a JSON encoded string
        @return the object created from the dictionary

        """
        return cls(state=StateHolder.states[d["state"]])

    @classmethod
    def from_sqlite(cls, text):
        """
        Create a StateHolder from the given text.

        @param text the state in textform
        @return the new StateHolder
        """
        return cls(state=StateHolder.states[text])


def one_or_more(amount, single_str, multiple_str):
    """
    Return a string which uses either the single or the multiple form.

    @param amount the amount to be displayed
    @param single_str the string for a single element
    @param multiple_str the string for multiple elements

    @return the string representation

    """
    if amount == 1:
        ret_str = single_str
    else:
        ret_str = multiple_str
    return ret_str % amount


def str_from_time_span(t_span):
    """
    Create a pretty string representation of a Time span.

    The function returns a string that is a natural representation
    of the time span. For example "1 day", "2 days", "3 hours", ...


    @return the string

    """
    if t_span.days < 0:
        raise
    if t_span.days > 0:
        return one_or_more(t_span.days, "%d day", "%d days")
    if t_span.seconds > 3600:
        return one_or_more(t_span.seconds // 3600, "%d hour", "%d hours")
    if t_span.seconds > 60:
        return one_or_more(t_span.seconds // 60, "%d minute", "%d minutes")
    return one_or_more(t_span.seconds, "%d second", "%d seconds")


class Date(serializer.JSONSerialize):

    """
    Date is the representation of a Task.

    All Date object store the date in a UTC format.

    """

    utc_id = "utc"
    local_tz = pytz.timezone(config.LOCAL_TZ)

    def __init__(self, date, local_tz=False):
        self._date = date
        if self._date.tzinfo:
            # _date has a time zone make it to utc
            self._date = self._date.astimezone(pytz.utc)
        elif local_tz:
            # _date has no timezone letz use the given timezone
            self._date = Date.local_tz.localize(self._date)
        else:
            raise AttributeError("The given date had no timezone data")

    def __get_tuple(self):
        return (self._date.year,
                self._date.month,
                self._date.day,
                self._date.hour,
                self._date.minute,
                self._date.second,
                self._date.microsecond)

    def get_local(self):
        """
        Return the date in local time.

        The method returns a datetime object which has the time
        of the local time zone.

        @return a datetime object with the current time zone

        """
        return self._date.astimezone(Date.local_tz)

    def json_serialize(self):
        """
        The method returns a dictionary which can be serialized into JSON.

        The dictionary returned by the message has the following form:
            {class, module, utc: [year, month, day, hour, minute, second, ms]}

        @return the dictionary created

        """
        return Date.create_dict({Date.utc_id: self.__get_tuple()})

    def __lt__(self, obj):
        return self._date <= Date._ret_date_or_obj(obj)

    def __le__(self, obj):
        return self._date <= Date._ret_date_or_obj(obj)

    def __eq__(self, obj):
        return self._date == Date._ret_date_or_obj(obj)

    def __ge__(self, obj):
        return self._date >= Date._ret_date_or_obj(obj)

    def __gt__(self, obj):
        return self._date > Date._ret_date_or_obj(obj)

    def __sub__(self, obj):
        return self._date - Date._ret_date_or_obj(obj)

    def __add__(self, obj):
        return self._date + Date._ret_date_or_obj(obj)

    def __str__(self):
        return str(self._date)

    def isoformat(self):
        return self._date.isoformat()

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return "%s" % self.isoformat()

    @classmethod
    def from_sqlite(cls, text):
        import dateutil.parser
        return Date(dateutil.parser.parse(text))

    def local_str(self):
        """
        Return the date as a string.

        @return the date as a localized string

        """
        return self.get_local().strftime(config.DATE_OUT_STR)

    @classmethod
    def from_json(cls, d):
        """
        Use the dictionary d and creates a new object of this class.

        The dictionary d needs to have the element
        utc:[year, month, day, hour, minute, second, ms]

        @param d the dictionary which was created from a JSON encoded string
        @return the Date object created from the dictionary

        """
        year, month, day, hour, minute, second, microsecs = d[Date.utc_id]
        date = datetime.datetime(year, month, day,
                                 hour, minute, second, microsecs, pytz.utc)
        return Date(date)

    @classmethod
    def local(cls, year, month, day, hour=0, minute=0, second=0, microsecond=0):
        """
        Create a Date object from local time zone data.

        @param year the year of the Date
        @param month the monthe of the Date
        @param day the day of the Date
        @param hour the hour of the Date (default = 0)
        @param minute the minute of the Date (default = 0)
        @param second the second of the Date (default = 0)
        @param microsecond the ms of the Date (default = 0)

        @return a new Date object

        """
        return Date(datetime.datetime(year, month, day, hour, minute, second,
                                      microsecond, tzinfo=Date.local_tz))

    @classmethod
    def local_from_str(cls, date_str):
        """
        Create a Date object from a string.

        The string needs to follow the format in config.DATE_INPUT_STR.

        @param date_str the string which will be parsed infor a date

        @return the new Date object

        """
        date = datetime.datetime.strptime(date_str, config.DATE_INPUT_STR)

        return Date(date, local_tz=Date.local_tz)

    @classmethod
    def now(cls, timezone=local_tz):
        """
        Return a Date object that has the current time.

        @param timezone the timezone of the Date object

        @return the Date object with the current time

        """
        return Date(datetime.datetime.now(timezone))

    @property
    def date(self):
        """
        Retrun the internal datetime object.

        @return the internal datetime object.

        """
        return self._date

    @staticmethod
    def _ret_date_or_obj(obj):
        """
        Return the obj or if date member variable.

        If the given object is a instance of Date the method returns
        the date member variable. If not the method return the given
        object reference.

        @param obj the object that is checked

        @return the obj or its date

        """
        if isinstance(obj, Date):
            return obj.date
        return obj


class TimeSpan(serializer.JSONSerialize):

    """
    TimeSpan is a class to represent a span of time with a start and an end.

    A TimeSpan object is used to store a time span with a start point of
    type Date and an end point of type Date. With this you can calculate
    the time difference between start and end.

    """

    def __init__(self, start=None, end=None):
        self._start = None
        self._end = None
        # call the setters of the properties (don't let it foul you)
        self.start = start
        self.end = end

    @property
    def start(self):
        """
        Return the start of the TimeSpan.

        @return the start a Date object

        """
        return self._start

    @start.setter
    def start(self, start):
        """
        Set the start date of the TimeSpan.

        @param start is a Date object

        """
        if start is not None:
            assert isinstance(start, Date), "The argument start is of type %r and not task.Date." % type(start)
            assert self._end is None or self._end >= start, "The start date must be older then the start date."
        self._start = start

    @property
    def end(self):
        """
        Get the end of the TimeSpan.

        @return the end which is a Date object

        """
        return self._end

    @end.setter
    def end(self, end):
        """
        Set the end of the TimeSpan.

        @param end the end of the time span

        """
        if end is not None:
            assert end is None or isinstance(end, Date), "The argument end is of type %r and not task.Date." % type(end)
            assert self._start is None or self._start <= end, "The end date must be newer then the start date."
        self._end = end

    def time_span(self):
        """
        Return the time span.

        The method returns the time difference between the start and end.

        @return the time difference which is a deltatime object

        """
        return self._end - self._start

    def __eq__(self, obj):
        return isinstance(obj, TimeSpan) and self.end == obj.end and self.start == obj.start

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            start_str = self.start.__conform__(protocol) if self.start else ""
            end_str = self.end.__conform__(protocol) if self.end else ""
            return "%s;%s" % (start_str, end_str)

    @classmethod
    def from_sqlite(cls, text):
        start_str, end_str = text.split(";")
        start = Date.from_sqlite(start_str) if start_str != "" else None
        end = Date.from_sqlite(end_str) if end_str != "" else None
        return cls(start=start, end=end)


class Task(serializer.JSONSerialize):

    """
    Super class of all tasks.

    Task implements the basic functionalaty of a task.

    """

    @staticmethod
    def create_table():
        return

    def __init__(self, title, description, task_id=None, created=Date.now(),
                 due=None, difficulty=DIFFICULTY.unknown, category=None, source=None,
                 state=StateHolder(), scheduled=TimeSpan(), real_schedule=TimeSpan()):
        self._task_id = task_id
        self._title = title
        self._description = description
        self._state = state
        self.difficulty = difficulty
        self._category = category
        self._source = source
        self._due = due
        self._created = created
        # Planned schedule holds the planned start and end
        self._scheduled = scheduled
        # In the real schedule the actual start and end time are stored
        self._real_schedule = real_schedule

    @property
    def task_id(self):
        return self._task_id

    @task_id.setter
    def task_id(self, obj):
        self._task_id = obj

    @property
    def title(self):
        return self._title

    @title.setter
    def title(self, obj):
        self._title = obj

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, obj):
        self._description = obj

    @property
    def state(self):
        return self._state

    @property
    def difficulty(self):
        return self._difficulty

    @difficulty.setter
    def difficulty(self, obj):
        if obj in DIFFICULTY.keys:
            self._difficulty = obj
        else:
            raise

    @property
    def category(self):
        return self._category

    @property
    def source(self):
        return self._source

    @property
    def due(self):
        return self._due

    @property
    def created(self):
        return self._created

    @property
    def scheduled(self):
        return self._scheduled

    @property
    def real_schedule(self):
        return self._real_schedule

    def __eq__(self, obj):
        return (isinstance(obj, Task)
                and self.title == obj.title
                and self.description == obj.description
                and self.state == obj.state
                and self.difficulty == obj.difficulty
                and self.due == obj.due
                and self.created == obj.created
                and self.category == obj.category
                and self.source == obj.source
                and self.scheduled == obj.scheduled
                and self.real_schedule == obj.real_schedule)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr((self.title, self.description, self.state, self.difficulty, self.due, self.category, self.source, self.scheduled, self.real_schedule))


class Store(object):

    """
    The Store class holds the list of tasks and is responsible for loading and saving them to a file.

    In addition the store can search throu the tasks and manage the tasks
    """

    version = "version"

    def __init__(self, filename, create=False):
        self._tasks = []
        self._new_tasks = []
        self._filename = filename
        self._decoder = serializer.TaskDecoder()
        self._encoder = serializer.TaskEncoder()
        self._version = 0
        if create:
            self.save()
        else:
            self.load()

    def load(self):
        fd = open(self._filename, "r")
        header = self._decoder.decode(fd.readline())
        self._tasks = self._decoder.decode(fd.read())
        self._version = header[Store.version]

    def save(self):
        new_header_str = self._encoder.encode({Store.version: self._version})
        self._tasks += self._new_tasks
        self._new_tasks = []
        new_task_str = self._encoder.encode(self._tasks)
        fd = open(self._filename, "w+", 4096)
        fd.write(new_header_str + "\n")
        fd.write(new_task_str)
        fd.close()
        self._saved = True

    def add(self, task):
        self._new_tasks.append(task)

    @property
    def saved(self):
        return len(self._new_tasks) == 0


class TWTask(Task):

    """A first taskwarrior task."""

    def __init__(self, task_dict):
        def get_attr(string, default):
            """Return the element at string if there of default."""
            if str in task_dict:
                return task_dict[string]
            else:
                return default

        def parse_time(s, d):
            """Parse the time stamp of a task warrior task."""
            return Date(datetime.datetime.strptime(d[s], "%Y%m%dT%H%M%SZ"), local_tz=True) if s in d else None

        _description = "description"
        Task.__init__(self, task_dict[_description][0:10], task_dict[_description],
                      created=parse_time("entry", task_dict),
                      due=parse_time("due", task_dict),
                      started=parse_time("start", task_dict)
                      )
        if "depends" in task_dict:
            self.depends = task_dict["depends"].split(",")
        else:
            self.depends = []

        self._id = task_dict["id"]
        self.uuid = task_dict["uuid"]
        self.urgency = task_dict["urgency"]

        self.end = get_attr("end", None)
        self.recur = get_attr("recur", None)
        self.tags = get_attr("tags", None)
        self.modified = get_attr("modified", None)
        self.project = get_attr("project", None)

        self.data = task_dict

    def __str__(self):
        return unicode("uuid: %s\n Name: %s \n(%s)\n\n %s" % (self.uuid, self.description, self.state, self.data))

    def __repr__(self):
        return "(%s, %s)" % (self.uuid, self.description)


class TaskwarrioirStore(object):

    """This class imports taskwarrior tasks."""

    def __init__(self):
        import json
        output = subprocess.check_output(["task", "export"])
        items = [TWTask(x) for x in json.loads("[" + output + "]")]
        self.index = dict((x.uuid, x) for x in items)
        self.pending = [x for x in items if x.state == "pending"]

    def get_tasks(self):
        """
        return the pending tasks.

        @return the pending task

        """
        return self.pending

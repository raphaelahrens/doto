# -*- coding: utf-8 -*-
"""
This module implements the all base classes for a task of the Done!Tools.

The task module implements all basic classes for the Done!Tools project.
It's a base for all future plug-ins.

"""

import datetime
import pytz
import sqlite3

import serializer
import statemachine


def create_difficulties(**difficulties):
    """
    Create the difficulty values for the task evaluation.

    @return a enum like type
    """
    keys = []
    names = {}
    for name, d_id in difficulties.iteritems():
        names[name] = d_id
        keys.append(d_id)
    keys.sort()
    names["keys"] = keys
    return type("Difficulty", (), names)


DIFFICULTY = create_difficulties(unknown=0,
                                 simple=1,
                                 easy=2,
                                 medium=3,
                                 hard=4
                                 )


def _add_new_state(states, key, name=None, cls=statemachine.State):
    """
    Add a new state to the dictionary and retrun the state.

    @param dir the dictionary to which the state will be added.
    @param key the key for the state
    @param name the name of the state

    @return the new state

    """
    state = cls(key, name)
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
    completed = _add_new_state(states, "c", "completed", statemachine.FinalState)
    pending = _add_new_state(states, "p", "pending")
    started = _add_new_state(states, "s", "started")
    blocked = _add_new_state(states, "b", "blocked")
    interrupted = _add_new_state(states, "i", "interrupted")
    pending.add_neighbor(started, "start")
    started.add_neighbor(completed, "complete")
    started.add_neighbor(blocked, "block")
    started.add_neighbor(interrupted, "interrupt")
    blocked.add_neighbor(started, "unblock")
    interrupted.add_neighbor(started, "restart")

    def __init__(self, state=pending):
        assert state.key in StateHolder.states
        self._state = state

    @property
    def state(self):
        """ Return the current state."""
        return self._state

    def key(self):
        return self._state.key

    def complete(self):
        if self._state is StateHolder.completed:
            return False
        self._state = StateHolder.completed
        return True

    def start(self):
        if self.state is not StateHolder.pending:
            return False
        self._state = StateHolder.started
        return True

    def reset(self):
        self._state = StateHolder.pending
        return True

    def next_state(self, action):
        """Set the next state according to the given action."""
        # TODO: unused in cli
        self._state = self._state.next_state(action)

    def get_actions(self):
        """
        Get all possible action from the current state.

        @return a list of the action for the current state.

        """
        # TODO: unused in cli
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
        # TODO: unused in cli
        return StateHolder.create_dict({"state": self.key()})

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return self.key()

    def __eq__(self, obj):
        if isinstance(obj, StateHolder):
            return self.key() == obj.key()
        return self.key() == obj

    def __str__(self):
        return self._state.name

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


class Date(serializer.JSONSerialize):

    """
    Date is the representation of a Task.

    All Date object store the date in a UTC format.

    """

    _utc_id = "utc"
    _local_tz = pytz.timezone(_utc_id)
    _local_input_str = "%Y.%m.%d-%H:%M"

    @staticmethod
    def set_local_tz(tz_str):
        Date._local_tz = pytz.timezone(tz_str)

    def __init__(self, date, local_tz=False):
        self._date = date
        if self._date.tzinfo:
            # _date has a time zone make it to utc
            self._date = self._date.astimezone(pytz.utc)
        elif local_tz:
            # _date has no timezone letz use the given timezone
            self._date = Date._local_tz.localize(self._date)
        else:
            raise AttributeError("The given date had no timezone data")

    def __get_tuple(self):
        """ Return a tuple with  the year, month, day, hour, minute, second, mircosecond."""
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
        return self._date.astimezone(Date._local_tz)

    def json_serialize(self):
        """
        The method returns a dictionary which can be serialized into JSON.

        The dictionary returned by the message has the following form:
            {class, module, utc: [year, month, day, hour, minute, second, ms]}

        @return the dictionary created

        """
        return Date.create_dict({Date._utc_id: self.__get_tuple()})

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

    def isoformat(self):
        """ Return the ISO-Format """
        return self._date.isoformat()

    def __conform__(self, protocol):
        if protocol is sqlite3.PrepareProtocol:
            return "%s" % self.isoformat()

    @classmethod
    def from_sqlite(cls, text):
        """Create a new Date objet from an sql-string."""
        import dateutil.parser
        return Date(dateutil.parser.parse(text))

    def local_str(self, format_str):
        """
        Return the date as a string.

        @return the date as a localized string

        """
        return self.get_local().strftime(format_str)

    @classmethod
    def from_json(cls, d):
        """
        Use the dictionary d and creates a new object of this class.

        The dictionary d needs to have the element
        utc:[year, month, day, hour, minute, second, ms]

        @param d the dictionary which was created from a JSON encoded string
        @return the Date object created from the dictionary

        """
        year, month, day, hour, minute, second, microsecs = d[Date._utc_id]
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
                                      microsecond, tzinfo=Date._local_tz))

    @classmethod
    def local_from_str(cls, date_str, local_format=_local_input_str):
        """
        Create a Date object from a string.

        The string needs to follow the format in the format argument.

        @param date_str the string which will be parsed infor a date

        @return the new Date object

        """
        date = datetime.datetime.strptime(date_str, local_format)

        return Date(date, local_tz=Date._local_tz)

    @classmethod
    def now(cls, timezone=_local_tz):
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
        """ Create a TimeSpan instacne form the given string. """
        start_str, end_str = text.split(";")
        start = Date.from_sqlite(start_str) if start_str != "" else None
        end = Date.from_sqlite(end_str) if end_str != "" else None
        return cls(start=start, end=end)


class Schedule(serializer.JSONSerialize):
    """
    Schedule holds all time components of a task.

    This includes the planned start and finishing point in time,
    the real start and finish point,
    and the due date, which tells us when the task must be done.
    """
    def __init__(self, planned=None, real=None, due=None):
        self._planned = planned if planned else TimeSpan()
        self._real = real if real else TimeSpan()
        self._due = due

    @property
    def planned(self):
        """
        Return the planned schedule.

        The planned schedule is of type TimeSpan and defines the planned start and end of a task.

        @return the planned schedule

        """
        return self._planned

    @property
    def real(self):
        return self._real

    @property
    def due(self):
        return self._due

    @due.setter
    def due(self, obj):
        self._due = obj

    def __eq__(self, obj):
        return (isinstance(obj, self.__class__)
                and self.planned == obj.planned
                and self.real == obj.real
                and self.due == obj.due
                )

    def finished_now(self):
        now = Date.now()
        self._real.end = now
        if not self._real.start:
            self._real.start = now

    def start_now(self):
        self._real.start = Date.now()

    def reset_now(self):
        self._real = TimeSpan()


class Task(serializer.JSONSerialize):

    """
    Super class of all tasks.

    Task implements the basic functionalaty of a task.

    """

    def __init__(self, title, description, task_id=None,
                 difficulty=DIFFICULTY.unknown, category=None,
                 ):
        self._task_id = task_id
        self._title = title
        self._description = description
        self._state = StateHolder()
        self._difficulty = difficulty
        self._category = category
        self._created = Date.now()
        self._schedule = Schedule()

    def set_internals(self, state, created, schedule):
        """
        Set the state, the date of creation and the schedule.

        All these members are only important when we load a task from file.
        For a new task these values are set by the constructor.

        @param state the state of the task
        @param created the date of creation of tis task
        @param schedule the schedule instance of this task

        """
        self._state = state
        self._created = created
        self._schedule = schedule

    @property
    def task_id(self):
        """ Returns the task_id for this task. """
        return self._task_id

    @task_id.setter
    def task_id(self, obj):
        """ Setter for the task_id. """
        self._task_id = obj

    @property
    def title(self):
        """ Returns the title string of the . """
        return self._title

    @title.setter
    def title(self, obj):
        """ The setter for the title string of this task. """
        self._title = obj

    @property
    def description(self):
        """ Return the description string of this task. """
        return self._description

    @description.setter
    def description(self, obj):
        """ Setter for the description string. """
        self._description = obj

    @property
    def state(self):
        """ Return the state of this task. """
        return self._state

    @property
    def difficulty(self):
        """ Return the difficulty of this task. """
        return self._difficulty

    @difficulty.setter
    def difficulty(self, obj):
        """
        Setter for the difficulty.

        The setter checks if the atribute obj is in DIFFICULTY.keys.

        @param obj a value in the range of DIFFICULTY.keys
        @throws AttributeError
        @return the difficulty of this task

        """
        if obj in DIFFICULTY.keys:
            self._difficulty = obj
        else:
            raise AttributeError("The given Difficulty is not in the range %s" % (str(DIFFICULTY.keys)))

    @property
    def category(self):
        """ Returns the category of this task. """
        return self._category

    @property
    def created(self):
        """ Returns the date when this task was created. """
        return self._created

    @property
    def schedule(self):
        """ Return the schedule of this task. """
        return self._schedule

    def done(self):
        """
        Finish the task.

        This method marks the task as completed and also sets the end date
        """
        if not self._state.complete():
            return False
        self._schedule.finished_now()
        return True

    def start(self):
        """
        Start the task.

        This method marks the task as started and also sets the start date
        """
        if not self._state.start():
            return False
        self._schedule.start_now()
        return True

    def reset(self):
        """
        Reset the tasks state.

        Set the state of the task to pending.
        """
        if not self._state.reset():
            return False
        self._schedule.reset_now()
        return True

    def __eq__(self, obj):
        return (isinstance(obj, Task)
                and self.title == obj.title
                and self.description == obj.description
                and self.state == obj.state
                and self.difficulty == obj.difficulty
                and self.created == obj.created
                and self.category == obj.category
                and self.schedule == obj.schedule)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return repr((self.task_id,
                     self.title,
                     self.description,
                     self.state,
                     self.difficulty,
                     self.category,
                     self.schedule
                     )
                    )


class Store(object):
    """
    The Store class holds the list of tasks and is responsible for loading and saving them to a file.

    In addition the store can search through the tasks and manage the tasks
    """

    def __init__(self, manager):
        self.__manager = manager
        self.__new_tasks = []
        self.__modified_tasks = []
        self.__deleted_tasks = []

    def get_tasks(self, cache=False, limit=10):
        return self.__manager.get_tasks(cache, limit=limit)

    def get_open_tasks(self, cache=False, limit=10):
        return self.__manager.get_tasks(cache, limit=limit, only_undone=True)

    def get_cache(self):
        return self.__manager.get_cache()

    def add_new(self, tsk):
        self.__new_tasks.append(tsk)

    def modify(self, tsk):
        self.__modified_tasks.append(tsk)

    def delete(self, tsk):
        self.__deleted_tasks.append(tsk)

    def is_saved(self):
        return not (self.__new_tasks or self.__modified_tasks or self.__deleted_tasks)

    def save(self):
        if self.__manager.save_new(self.__new_tasks):
            del self.__new_tasks[:]
        if self.__manager.update(self.__modified_tasks):
            del self.__modified_tasks[:]
        if self.__manager.delete(self.__deleted_tasks):
            del self.__deleted_tasks[:]

        return self.is_saved()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.__manager.close()


class JSONManager(object):

    version = "version"

    def __init__(self, filename, create=False):
        # TODO: unused in cli
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
        """ Load task from the file. """
        # TODO: unused in cli
        file_handle = open(self._filename, "r")
        header = self._decoder.decode(file_handle.readline())
        self._tasks = self._decoder.decode(file_handle.read())
        self._version = header[JSONManager.version]

    def save(self):
        """ Save all changes to file. """
        new_header_str = self._encoder.encode({JSONManager.version: self._version})
        self._tasks += self._new_tasks
        self._new_tasks = []
        new_task_str = self._encoder.encode(self._tasks)
        file_handle = open(self._filename, "w+", 4096)
        file_handle.write(new_header_str + "\n")
        file_handle.write(new_task_str)
        file_handle.close()
        self._saved = True

    def add(self, task):
        """ Add a new task to the store. """
        # TODO: unused in cli
        self._new_tasks.append(task)

    @property
    def saved(self):
        """Return True if all values were saved."""
        # TODO: unused in cli
        return len(self._new_tasks) == 0

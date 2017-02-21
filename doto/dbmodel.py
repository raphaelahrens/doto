# -*- coding: utf-8 -*-
"""
This module implements the all base classes for a task of the Done!Tools.

The task module implements all basic classes for the Done!Tools project.
It's a base for all future plug-ins.

"""

import pickle
import collections
import datetime
import pytz

import sqlalchemy.ext.declarative
import sqlalchemy.ext.mutable
import sqlalchemy.orm
import doto.statemachine

Base = sqlalchemy.ext.declarative.declarative_base()


def now_with_tz():
    """
    Get the current time in UTC format.

    @return the current time
    """
    return datetime.datetime.now(tz=pytz.utc)


def create_difficulties(**difficulties):
    """
    Create the difficulty values for the task evaluation.

    @return a enum like type
    """
    keys = []
    names = {}
    for name, d_id in difficulties.items():
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


def _add_new_state(states, key, name=None, cls=doto.statemachine.State):
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


class StateHolder(sqlalchemy.ext.mutable.MutableComposite):

    """
    This class is used to manage the state of a Task object.

    The StateHolder class holds the current state of the task and supports
    methods to manipulate the state of the task.

    Supported states are pending, started, completed, blocked, interrupted.

    """

    states = {}
    completed = _add_new_state(states, "c", "completed", doto.statemachine.FinalState)
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

    @property
    def key(self):
        """ Return the key of the state. """
        return self._state.key

    @state.setter
    def state(self, value):
        """ Set the state of the task. """
        self._state = value
        self.changed()

    def complete(self):
        """ Set the state to complete if itis not already complete. """
        if self.state is StateHolder.completed:
            return False
        self.state = StateHolder.completed
        return True

    def start(self):
        """ Set the state to started if it is not already started.  """
        if self.state is not StateHolder.pending:
            return False
        self.state = StateHolder.started
        return True

    def reset(self):
        """ Reset the state to pending. """
        self.state = StateHolder.pending
        return True

    def next_state(self, action):
        """Set the next state according to the given action."""
        # TODO: unused in cli maybe in gui
        self.state = self._state.next_state(action)

    def get_actions(self):
        """
        Get all possible action from the current state.

        @return a list of the action for the current state.

        """
        # TODO: unused in cli
        return self.state.get_actions()

    def __eq__(self, obj):
        if isinstance(obj, StateHolder):
            return self.key == obj.key
        return self.state == obj

    def __hash__(self):
        return hash(self.key)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return self.state.name

    def __repr__(self):
        return "StateHolder(state=%s)" % self.state.name

    def __composite_values__(self):
        return (self.state, )


class StateHolderComp(sqlalchemy.orm.CompositeProperty.Comparator):
    """ Comparator class for the state of a Task object. """
    def __eq__(self, other):
        """redefine the 'equal' operator"""

        if isinstance(other, doto.statemachine.AbstractState):
            return sqlalchemy.sql.and_(*[a == b for a, b in
                                       zip(self.__clause_element__().clauses,
                                           (other,))])

        return sqlalchemy.sql.and_(*[a == b for a, b in
                                   zip(self.__clause_element__().clauses,
                                       other.__composite_values__())])


class StateType(sqlalchemy.TypeDecorator):
    """
    The Database type for the StateHolder objects.
    """
    impl = sqlalchemy.Enum

    def process_bind_param(self, value, _):
        """
        Store the key value of the State object so it wil be stre in the DB.
        """
        return value.key

    def process_result_value(self, value, _):
        """
        Return the State object from StateHolder.states that matches the value.
        """
        return StateHolder.states[value]

    def python_type(self):
        """
        Return the Python type of this Database type.
        """
        return doto.statemachine.State


class UTCDateTime(sqlalchemy.types.TypeDecorator):
    """
    TypeDecorator for the DateTime type so all timestamps have the UTC timezone
    """

    impl = sqlalchemy.DateTime

    def process_bind_param(self, value, _):
        """
        Store timestamp in UTC.
        """
        if value is not None:
            return value.astimezone(pytz.utc)

    def process_result_value(self, value, _):
        """
        Return timestamp in UTC.
        """
        if value is not None:
            return pytz.utc.localize(value)

    def python_type(self):
        """
        Return the implementation type.
        """
        return UTCDateTime.impl.python_type


class TimeSpan(sqlalchemy.ext.mutable.MutableComposite):

    """
    TimeSpan is a class to represent a span of time with a start and an end.

    A TimeSpan object is used to store a time span with a start point of
    type Date and an end point of type Date. With this you can calculate
    the time difference between start and end.

    """

    def __init__(self, start=None, end=None, end_delta=None):
        """
        Create a TimeSpan object where the begin of the time span is `start`
        and the end of it is either set with `end` or `end_delta`.

        If `end` is `None` and `end_delta` isn't then the end of the time span
        will be set to `start + end_delta`.

                Code shitt bla

        LOL

        @param start The begin of the time span.
        @param end The end of the time span.
        @param end_delta Alternative set the end with timedelta.
        """
        self._start = None
        self._end = None
        # call the setters of the properties (don't let it foul you)
        self.start = start
        if end:
            self.end = end
        elif end_delta:
            self.end = start + end_delta

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
        if start is not None and self._end is not None and self._end < start:
            raise ValueError("The start date is older then start date")
        self._start = start
        self.changed()

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
        if self.start is None and end is not None:
            raise ValueError("There must be a start value first")
        if end is not None and self._start > end:
            raise ValueError("The end date must be newer then the start date.")
        self._end = end
        self.changed()

    def time_delta(self):
        """
        Return the time span.

        The method returns the time difference between the start and end.

        @return the time difference which is a deltatime object

        """
        return self._end - self._start

    def __keys(self):
        return (self.end, self.start)

    def __eq__(self, obj):
        return isinstance(obj, TimeSpan) and self.__keys() == obj.__keys()

    def __hash__(self):
        return hash(self.__keys())

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __composite_values__(self):
        return self._start, self._end

    def __repr__(self):
        return "TimeSpan(start=%r, end=%r" % (self.start, self.end)


class Event(object):
    """
    An event everything that can beplanned with Done!Tools

    It is the superclass of Task and Appointment.

    """

    event_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.Unicode, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.Unicode, nullable=True)
    created = sqlalchemy.Column(UTCDateTime(timezone=True), nullable=False)

    def __init__(self, title, description):
        self.title = str(title)
        self.description = str(description) if description else ""
        self.created = now_with_tz()
        self.cache_id = None

    def __repr__(self):
        return ("%s(title=%r, description=%r)" %
                (self.__class__.__name__,
                    self.title,
                    self.description
                 )
                )


class Timerecord(Base):

    """
    A timerecord is a time span for which one worked on a task

    A timerecord is a time span that is assosiated with a event.
    The sum of all timerecords is the total amount of work taht was put into the Task.

    This can be used to track the amount of time one worked a specific task.
    This should come in handy for freelancers (like me).
    """

    __tablename__ = "timerecord"

    tr_id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    event_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tasks.event_id'), nullable=True)
    _start = sqlalchemy.Column("start", UTCDateTime(timezone=True), nullable=True)
    _end = sqlalchemy.Column("end", UTCDateTime(timezone=True), nullable=True)
    span = sqlalchemy.orm.composite(TimeSpan, _start, _end)

    def __init__(self, start, end=None, event=None):
        """
        """
        self.span = TimeSpan(start=start, end=end)
        self.event_id = event


class Task(Event, Base):

    """
    Super class of all tasks.

    Task implements the basic functionality of a task.

    """
    __tablename__ = "tasks"

    _state = sqlalchemy.Column("state", StateType(*StateHolder.states.keys()), nullable=False)
    _difficulty = sqlalchemy.Column("difficulty", sqlalchemy.Integer, nullable=False)
    due = sqlalchemy.Column("due", UTCDateTime(timezone=True), nullable=True)
    _real_start = sqlalchemy.Column("real_start", UTCDateTime(timezone=True), nullable=True)
    _real_end = sqlalchemy.Column("real_end", UTCDateTime(timezone=True), nullable=True)

    timerecords = sqlalchemy.orm.relationship("Timerecord")

    state = sqlalchemy.orm.composite(StateHolder, _state, comparator_factory=StateHolderComp)
    real_sch = sqlalchemy.orm.composite(TimeSpan, _real_start, _real_end)

    def __init__(self, title, description,
                 difficulty=DIFFICULTY.unknown
                 ):
        Event.__init__(self, title, description)
        self.state = StateHolder()
        self.difficulty = difficulty
        self.real_sch = TimeSpan()
        self.due = None

    @property
    def difficulty(self):
        """ Get the difficulty of the task. """
        return self._difficulty

    @difficulty.setter
    def difficulty(self, obj):
        """ Set the difficulty of the task. """
        if obj not in DIFFICULTY.keys:
            raise ValueError
        self._difficulty = obj

    def done(self):
        """
        Finish the task.

        This method marks the task as completed and also sets the end date
        """
        if not self.state.complete():
            return False
        now = now_with_tz()
        if self.real_sch.start is None:
            self.real_sch.start = now

        self.real_sch.end = now

        return True

    def start(self):
        """
        Start the task.

        This method marks the task as started and also sets the start date
        """
        if not self.state.start():
            return False
        self.real_sch.start = now_with_tz()
        return True

    @property
    def started(self):
        return self.state.state is StateHolder.started

    def reset(self):
        """
        Reset the tasks state.

        Set the state of the task to pending.
        """
        if not self.state.reset():
            return False
        self.real_sch = TimeSpan()
        return True

    def __key(self):
        return (self.title,
                self.description,
                self.state,
                self.difficulty,
                self.created,
                self.real_sch,)

    def __eq__(self, obj):
        return isinstance(obj, Task) and self.__key() == obj.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return ((Event.__repr__(self)[:-1] + ",state=%r, difficulty=%r)") %
                (self.state,
                 self.difficulty)
                )


class Appointment(Event, Base):
    """
    An appointment (APMT) has a fixed starting date and cannot be started or finished.

    """

    __tablename__ = "appointments"

    _sch_start = sqlalchemy.Column("sch_start", UTCDateTime(timezone=True), nullable=False)
    _sch_end = sqlalchemy.Column("sch_end", UTCDateTime(timezone=True), nullable=True)

    schedule = sqlalchemy.orm.composite(TimeSpan, _sch_start, _sch_end)

    def __init__(self, title, start,
                 description=None, end=None
                 ):
        Event.__init__(self, title, description)
        self.__description = description
        self.schedule = TimeSpan(start, end)

    def move(self, start, end=None):
        """
        Move the appointment to a new start and/or end date


        @param start the new starting date
        @param end the new end of the appointment. Default=None

        """
        if end is not None and start >= end:
            return False

        self.schedule.start = start
        self.schedule.end = end
        return True

    def __repr__(self):
        return ("%s(title=%r, description=%r, start=%r, end=%r)" %
                (self.__class__.__name__,
                 self.title,
                 self.description,
                 self.schedule.start,
                 self.schedule.end
                 )
                )

CacheItem = collections.namedtuple("CacheItem", ["event_id", "event_type"])


def dump_cache(filename, events):
    """
    Dump the Cache in the given file.

    @param filename the name of the file
    @param events the events that will be stored in the cache.
    """
    with open(filename, "wb") as cache_file:
        pickle.dump([CacheItem(event.event_id, event.__class__) for event in events],
                    cache_file,
                    protocol=pickle.HIGHEST_PROTOCOL)


def load_cache(filename):
    """
    Load the cache from the cache file.

    @param filename the name of the file

    @return the cache as a list of events.
    """
    try:
        with open(filename, "rb") as cache_file:
            return pickle.load(cache_file), False
    except IOError:
        return [], True


def _create_dir(db_name):
    """
    Create the whole directory path to the database file if necessary.

    @param db_name the complete path to the database file
            It can be a local path.
    """
    import errno
    import os
    dir_path = os.path.dirname(db_name)
    try:
        os.makedirs(dir_path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise exception


class Store(object):
    """
    The Store class holds the list of events and is responsible for loading and saving.

    In addition the store can search through the tasks and manage the tasks
    """

    def __init__(self, filename, cache_file, debug=False):
        if filename == "":
            eng_str = "sqlite://"
        else:
            _create_dir(filename)
            eng_str = "sqlite:///" + filename
        engine = sqlalchemy.create_engine(eng_str, echo=debug)
        self.session = sqlalchemy.orm.sessionmaker(bind=engine)()
        Base.metadata.create_all(engine)

        self.__cache = False
        self.__cache_file = cache_file
        self._cache_list = []

    def enable_caching(self):
        """ Enable the caching for this store. """
        self.__cache = True

    @staticmethod
    def _get_limit(query, limit):
        """
        A helper function that uses the right method call depending on the given limit.

        @param limit if it is smaller then zero all events will be returned
                if it is above zero only limit events will be returned.
        """
        if limit <= 0:
            return query.all()
        else:
            return query[:limit]

    def _add_to_cache(self, events):
        """
        Add the events to the cache.

        @param events the events that will be added to the cache.
        """
        cache_len = len(self._cache_list)
        for i, event in enumerate(events):
            event.cache_id = cache_len + i

        if self.__cache:
            self._cache_list += events

    def get_tasks(self, limit=10):
        """
        Get a list of all tasks.

        @param cache if True the result will be stored in the cache
                so a cache_id can be used. Default=False
        @param limit Set the maximum number of returned items. Default=10
                If limit is zero there is no limit

        """
        tasks = Store._get_limit(self.session.query(Task), limit)
        self._add_to_cache(tasks)

        return tasks

    def get_started_timerecords(self):
        """
        """
        record = self.session.query(Timerecord).filter(
            Timerecord._end == None
        ).all()

        return record

    def get_apmts(self, date, delta):
        """
        Get the appointments that are between the given date and the date + delta.

        So to get the appointments of the next seven days set date to now and delta to seven days.

        @param date The returned appointments are younger then this date.
        @param delta Only Appointments that are older than date + delta are returned.

        @return the appointments between the date and date + delta
        """
        apmts = self.session.query(Appointment).filter(
            sqlalchemy.and_(
                Appointment._sch_start >= date,
                Appointment._sch_start < (date + delta))
        ).all()
        self._add_to_cache(apmts)
        return apmts

    def get_task_count(self):
        """ Get the count Tasks in the database. """
        return self.session.query(Task).count()

    def get_apmt_count(self):
        """ Get the count Tasks in the database. """
        return self.session.query(Appointment).count()

    def get_open_tasks(self, limit=20):
        """
        Get all task which are not completed.

        @param cache if True the result will be stored in the cache
                so a cache_id can be used. Default=False
        @param limit Set the maximum number of returned items. Default=10

        @return A list of unfinished tasks
        """
        tasks = Store._get_limit(self.session.query(Task).filter(Task.state != StateHolder.completed), limit)
        self._add_to_cache(tasks)

        return tasks

    def get_cache(self):
        """
        Get all elements in the cache.

        This methode gets used by the cli commandsr
        which can use the cahe_id.

        """
        return load_cache(self.__cache_file)

    def __get_cache_item(self, cache_id, query):
        """
        Get the Item with the id cache_id from the cache.

        @param cache_id the id of the cache item

        @return the cache item that matches the given id or None.
        """
        cache, cache_error = self.get_cache()

        if cache_error or cache_id < 0 or cache_id > len(cache):
            return None, cache_error

        item = cache[cache_id]

        return query(item), cache_error

    def get_cache_item(self, cache_id):
        """
        Get the Item with the id cache_id from the cache.

        @param cache_id the id of the cache item

        @return the cache item that matches the given id or None.
        """
        def query(item):
            return self.session.query(item.event_type).get(item.event_id)
        return self.__get_cache_item(cache_id, query)

    def get_cache_task(self, cache_id):
        def query(item):
            return self.session.query(Task).get(item.event_id)
        return self.__get_cache_item(cache_id, query)

    def get_cache_apmt(self, cache_id):
        def query(item):
            return self.session.query(Appointment).get(item.event_id)
        return self.__get_cache_item(cache_id, query)

    def add_new(self, event):
        """
        Add a new event to the store
        it will be saved when self.save gets called.

        @param event the new event
        """
        if isinstance(event, collections.Iterable):
            self.session.add_all(event)
        else:
            self.session.add(event)

    def delete(self, event):
        """
        Delete an event from the store

        @param event the event that will be deleted
        """
        try:
            self.session.delete(event)
            return True
        except sqlalchemy.exc.InvalidRequestError:
            return False

    @property
    def is_saved(self):
        """ Return True if the was already saved. """
        return not (self.session.deleted or self.session.dirty or self.session.new)

    def save(self):
        """
        Save the store.

        @returns True if the save worked flawless
        """
        self.session.commit()

    def close(self):
        """
        Close the connection to the database and clean up.

        If the cache was enabled also save the cache to disk.
        """
        if self.__cache:
            dump_cache(self.__cache_file, self._cache_list)

        self.session.close()

    def __enter__(self):
        return self

    def __exit__(self, exit_type, value, traceback):
        self.close()

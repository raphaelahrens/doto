import collections
import datetime
import pickle
import sqlite3
import importlib

import pytz


def adapt_datetime(dt):
    utc_dt = pytz.utc.normalize(dt)
    return round(utc_dt.timestamp())


def convert_datetime(str_dt):
    return datetime.datetime.fromtimestamp(int(str_dt), tz=pytz.utc)


def setup_module(create_cmd, type_list):
    Store.CREATE_CMDS.add(create_cmd)

    sqlite3.register_adapter(datetime.datetime, adapt_datetime)
    sqlite3.register_converter('TIMESTAMP', convert_datetime)
    for cls, adapter, converter in type_list:
        sqlite3.register_adapter(cls, adapter)
        sqlite3.register_converter(cls.__name__, converter)


def now_with_tz():
    """
    Get the current time in UTC format.

    @return the current time
    """
    # remove the micrsoseconds before return
    n = datetime.datetime.now(tz=pytz.utc)
    return n - datetime.timedelta(microseconds=n.microsecond)


def get_foreign_obj(store, id, module):
    if id is None:
        return None
    return module.get(store, id)


def unwrap_row(store, row, cls, arg_list, opt_list=None, foreign_keys=None):
    if opt_list is None:
        opt_list = ()
    if foreign_keys is None:
        foreign_keys = ()
    args = {k: v for k, v in zip(row.keys(), row) if k in arg_list}

    foreign_args = {key: get_foreign_obj(store, row[key], module) for key, module in foreign_keys}
    args.update(foreign_args)
    obj = cls(**args)

    for opt in opt_list:
        if opt in row.keys():
            setattr(obj, opt, row[opt])
    return obj


def get_id(obj):
    if obj is None:
        return None
    return obj.id


def unwrap_obj(obj, ignore_list=None, foreign_keys=None):
    def member_gen(obj, ignore_list):
        for name in dir(obj):
            name_attr = getattr(obj, name)
            if name.startswith('_') or name in ignore_list or callable(name_attr):
                continue
            if name in foreign_keys:
                yield name, get_id(name_attr)
            else:
                yield name, name_attr

    if ignore_list is None:
        ignore_list = ()
    if foreign_keys is None:
        foreign_keys = ()

    return dict(member_gen(obj, ignore_list))


class TimeSpan(object):
    """
    TimeSpan is a class to represent a span of time with a start and an end.

    A TimeSpan object is used to store a time span with a start point of
    type Date and an end point of type Date. With this you can calculate
    the time difference between start and end.

    """

    def __init__(self, start=None, end=None):
        """
        Create a TimeSpan object where the begin of the time span is `start`
        and the end of it is either set with `end` or `end_delta`.

        If `end` is `None` and `end_delta` isn't then the end of the time span
        will be set to `start + end_delta`.

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

    def __init__(self, title, description, created=None):
        self.id = None
        self.title = title
        self.description = description if description else ""
        self.created = now_with_tz() if created is None else created
        self.cache_id = None

    def __repr__(self):
        return ("%s(title=%r, description=%r)" %
                (self.__class__.__name__,
                    self.title,
                    self.description
                 )
                )


CacheItem = collections.namedtuple('CacheItem', ['id', 'type', 'module'])


def dump_cache(filename, events):
    """
    Dump the Cache in the given file.

    @param filename the name of the file
    @param events the events that will be stored in the cache.
    """
    with open(filename, 'wb') as cache_file:
        pickle.dump([CacheItem(event.id, event.__class__, event.__class__.__module__)
                     for event in events],
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


def get_cache_item(store, cache_id, e_type):
    '''
    Get the item with cache_id from the cache file and return it.
    '''
    if cache_id < 0:
        return None, False
    cache, cache_error = load_cache(store.cache_file)
    if cache_error:
        return None, cache_error
    cache_item = cache[cache_id]
    if cache_item.type != e_type:
        return None, cache_error
    event_module = importlib.import_module(cache_item.module)
    event = event_module.get(store, cache_item.id)
    return event, cache_error


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
    CREATE_CMDS = set()

    def __init__(self, filename, cache_file):
        if filename != "":
            _create_dir(filename)
        else:
            filename = ':memory:'

        self.conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.conn.row_factory = sqlite3.Row

        self.cur = self.conn.cursor()
        self.create()

        self.cache_file = cache_file
        self._cache_list = []

    def create(self):
        create_cmds = ';'.join(Store.CREATE_CMDS)
        self.cur.executescript(create_cmds)

    def execute(self, query, parameters=None):
        if parameters is None:
            return self.cur.execute(query)
        return self.cur.execute(query, parameters)

    def get_one(self, convert, query, parameters=None):
        cur = self.execute(query, parameters)
        row = cur.fetchone()
        assert cur.fetchone() is None
        return convert(row, self)

    def query(self, convert, query, parameters=None):
        cur = self.execute(query, parameters)
        return list(map(lambda x: convert(x, self), cur))

    def add_to_cache(self, events):
        """
        Add the events to the cache.

        @param events the events that will be added to the cache.
        """
        cache_len = len(self._cache_list)
        for i, event in enumerate(events):
            event.cache_id = cache_len + i

        self._cache_list += events

    def get_cache(self):
        """
        Get all elements in the cache.

        This methode gets used by the cli commandsr
        which can use the cahe_id.

        """
        return load_cache(self.cache_file)

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

    def save(self):
        """
        Save the store.

        @returns True if the save worked flawless
        """
        if len(self._cache_list) > 0:
            dump_cache(self.cache_file, self._cache_list)

        self.conn.commit()

    def close(self):
        """
        Close the connection to the database and clean up.

        If the cache was enabled also save the cache to disk.
        """
        self.cur.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exit_type, value, traceback):
        self.close()

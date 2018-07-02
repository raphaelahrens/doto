'''
Description of a calendar which groups appointments
'''
import doto.model
import doto.model.crud
from dateutil import rrule
import pytz

CREATE_CMD = '''
             CREATE TABLE IF NOT EXISTS
                calendars (
                     id INTEGER NOT NULL,
                     name TEXT NOT NULL,
                     url TEXT,
                     remote TEXT,
                     sync INTEGER,
                     PRIMARY KEY (id)
             );
             '''


class Calendar(object):
    '''
    A Calendar groups appointments together and

    It indicates that the event will repeat in a specific pattern.
    '''

    def __init__(self, name, url=None, remote=None, sync=False):
        ''' constructor for Repeat '''
        self.name = name
        self.url = url
        self.remote = remote
        self.sync = sync

    @staticmethod
    def row_to_obj(row, store):
        ''' Create Repeat from database row '''
        repeat = doto.model.unwrap_row(store,
                                       row,
                                       Calendar,
                                       ('name', ''),
                                       )
        return repeat

    @staticmethod
    def obj_to_row(obj):
        '''
        Create Row from repeat object
        '''
        row_dict = doto.model.unwrap_obj(obj)
        return row_dict

    def next(self, after_dt):
        ''' return the next event after after_dt '''
        utc_after = pytz.utc.normalize(after_dt).replace(tzinfo=None)
        return self.repeat_rule.after(utc_after).replace(tzinfo=pytz.utc)

    def __eq__(self, obj):
        return str(self.repeat_rule) == str(obj.repeat_rule)

    def __str__(self):
        return ''


insert_query = '''INSERT INTO calendars ( name,  url,  remote,  sync)
                                 VALUES (:name, :url, :remote, :sync);
               '''
update_query = '''UPDATE calendars SET name = :name,
                                       url = :url,
                                       remote = :remote,
                                       sync = :sync
                                      WHERE id = :id;
               '''
delete_query = '''DELETE FROM calendars WHERE id = ?;'''
select_query = '''SELECT * FROM calendars WHERE id = :id; '''

update = doto.model.crud.update(update_query, Calendar)
add_new = doto.model.crud.insert(insert_query, Calendar)
delete = doto.model.crud.delete(delete_query)
get = doto.model.crud.get(select_query, Calendar)


def convert_rrule(rule_str):
    return rrule.rrulestr(rule_str.decode('utf-8'))


doto.model.setup_module(CREATE_CMD, ((rrule.rrule, str, convert_rrule),))

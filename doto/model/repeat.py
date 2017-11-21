'''
Description of a recurring event.
'''
import doto.model
import doto.model.crud
from dateutil import rrule
import pytz

CREATE_CMD = '''
             CREATE TABLE IF NOT EXISTS
                repeats (
                     id INTEGER NOT NULL,
                     repeat_rule rrule NOT NULL,
                     event INTEGER, -- id of the event either a task or apmt
                     PRIMARY KEY (id)
             );
             '''

PATTERNS = {
        '@yearly':    rrule.YEARLY,
        '@monthly':   rrule.MONTHLY,
        '@weekly':    rrule.WEEKLY,
        '@daily':     rrule.DAILY,
        '@hourly':    rrule.HOURLY,
        }
REV_PATTERNS = {
        rrule.YEARLY: '@yearly',
        rrule.MONTHLY: '@monthly',
        rrule.WEEKLY: '@weekly',
        rrule.DAILY: '@daily',
        rrule.HOURLY: '@hourly',
        }


class Repeat(object):
    """
    A Repeat is meta data for a task with due date or an appointment

    It indicates that the event will repeat in a specific pattern.
    """

    def __init__(self, repeat_rule, event):
        ''' constructor for Repeat '''
        self.event = event

        self.repeat_rule = repeat_rule

    @staticmethod
    def row_to_obj(row, store):
        ''' Create Repeat from database row '''
        repeat = doto.model.unwrap_row(store,
                                       row,
                                       Repeat,
                                       ('repeat_rule', 'event'),
                                       ('id',)
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
        return REV_PATTERNS[self.repeat_rule._freq]


def parse(rule_pattern, start_dt, event):
    utc_start = pytz.utc.normalize(start_dt)
    return Repeat(rrule.rrule(PATTERNS[rule_pattern], dtstart=utc_start), event=event)


insert_query = '''INSERT INTO repeats ( repeat_rule,  event)
                              VALUES  (:repeat_rule, :event);
               '''
update_query = '''UPDATE repeats SET repeat_rule = :repeat_rule,
                                     event = :event
                                     WHERE id = :id;
               '''
delete_query = 'DELETE FROM repeats WHERE id = ?;'
select_query = '''SELECT * FROM repeats WHERE id = :id; '''

update = doto.model.crud.update(update_query, Repeat)
add_new = doto.model.crud.insert(insert_query, Repeat)
delete = doto.model.crud.delete(delete_query)
get = doto.model.crud.get(select_query, Repeat)


def convert_rrule(rule_str):
    return rrule.rrulestr(rule_str.decode("utf-8"))

doto.model.setup_module(CREATE_CMD, ((rrule.rrule, str, convert_rrule),))

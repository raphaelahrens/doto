'''
Description of a recurring event.
'''
import doto.model
import doto.model.crud
from dateutil import rrule

CREATE_CMD = '''
             CREATE TABLE IF NOT EXISTS
                repeats (
                     id INTEGER NOT NULL,
                     repeat_rule rrule NOT NULL,
                     event INTEGER, -- id of the event either a task or apmt
                     PRIMARY KEY (id)
             );
             '''


class Repeat(object):
    """
    A Repeat is meta data for a task with due date or an appointment

    It indicates that the event will repeat in a specific pattern.
    """

    def __init__(self, repeat_rule, event):
        """
        """
        self.event = event

        self.repeat_rule = repeat_rule

    @staticmethod
    def row_to_obj(row, store):
        '''
        Create Repeat from database row
        '''
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

    def next(self, dt):
        return self.repeat_rule.after(dt)

    def __eq__(self, obj):
        return str(self.repeat_rule) == str(obj.repeat_rule)


def parse(rule_pattern, start_dt, event):
    patterns = {
            '@yearly':    rrule.YEARLY,
            '@monthly':   rrule.MONTHLY,
            '@weekly':    rrule.WEEKLY,
            '@daily':     rrule.DAILY,
            '@hourly':    rrule.HOURLY,
            }
    return Repeat(rrule.rrule(patterns[rule_pattern], dtstart=start_dt), event=event)


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

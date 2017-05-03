'''
Description of a reocurring event.
'''
import doto.model

CREATE_CMD = '''
             CREATE TABLE IF NOT EXISTS
                repeats (
                     id INTEGER NOT NULL,
                     minute INTEGER,
                     hour INTEGER,
                     day INTEGER,
                     month INTEGER,
                     dow INTEGER,
                     PRIMARY KEY (id),
             )
             '''


class Repeat(object):
    """
    A Repeat is meta data for a task with due date or an appointment

    It indicates that the event will repeat in a specific pattern.
    """

    def __init__(self, repeat_pattern, dt):
        """
        """
        self.id = None

        self.minute = None
        self.hour = None
        self.day = None
        self.month = None
        self.dow = None  # Day of week 0 (SUN) - 7 (SA)

        min = dt.minute
        hour = dt.hour
        day = dt.day
        month = dt.month
        dow = dt.weekday()

        patterns = {
                '@yearly':    (min, hour,  day, month, None),
                '@monthy':    (min, hour,  day,  None, None),
                '@weekly':    (min, hour, None,  None,  dow),
                '@daily':     (min, hour, None,  None, None),
                '@hourly':    (min, None, None,  None, None),
                }

        self.set_values(*patterns[repeat_pattern])

    def set_values(self, minute, hour, day, month, dow):
        self.minute = minute
        self.hour = hour
        self.day = day
        self.month = month
        self.dow = dow  # Day of week 0 (SUN) - 7 (SA)

    @staticmethod
    def row_to_obj(row, _):
        '''
        Create Task from database row
        '''
        repeat = doto.model.unwrap_row(row,
                                       Repeat,
                                       ('id',))
        return repeat

    @staticmethod
    def obj_to_row(obj):
        '''
        Create Row from repeat object
        '''
        row_dict = doto.model.unwrap_obj(obj, ignore_list=[])
        return row_dict


insert_query = '''INSERT INTO repeats (minute, hour, day, month, dow)
                              VALUES  (:minute, :hour, :day, :month, :dow)
                  ;
               '''
update_query = '''UPDATE repeats SET minute = :minute
                                     hour = :hour,
                                     day = :day,
                                     month = :month,
                                     dow = :dow
                                     WHERE id = :id;
               '''
delete_query = 'DELETE FROM repeats WHERE id = ?;'
select_query = '''SELECT * FROM repeats WHERE id = :id; '''

update = doto.model.crud.update(update_query, Repeat)
add_new = doto.model.crud.insert(insert_query, Repeat)
delete = doto.model.crud.delete(delete_query)
get = doto.model.crud.get(select_query, Repeat)

doto.model.setup_module(CREATE_CMD, ())

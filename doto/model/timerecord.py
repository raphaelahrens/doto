import doto.model
import doto.model.task

CREATE_CMD = """
             CREATE TABLE IF NOT EXISTS
                timerecords (
                     id INTEGER NOT NULL,
                     task_id INTEGER,
                     start TIMESTAMP,
                     end TIMESTAMP,
                     PRIMARY KEY (id),
                     FOREIGN KEY(task_id) REFERENCES tasks (id)
             )
             """


class Timerecord(object):
    """
    A timerecord is a time span for which one worked on a task

    A timerecord is a time span that is assosiated with a event.
    The sum of all timerecords is the total amount of work taht was put into the Task.

    This can be used to track the amount of time one worked a specific task.
    This should come in handy for freelancers (like me).
    """

    def __init__(self, start, end=None, task_event=None):
        """
        """
        self.id = None
        self.span = doto.model.TimeSpan(start=start, end=end)
        self.task = task_event

    @staticmethod
    def row_to_obj(row, store):
        """
        Create Task from database row
        """
        timerecord = doto.model.unwrap_row(store,
                                           row,
                                           Timerecord,
                                           ('start', 'end'),)
        task_id = row['task_id']
        if task_id is None:
            timerecord.task = None
        else:
            timerecord.task = doto.model.task.get(store, task_id)
        return timerecord

    @staticmethod
    def obj_to_row(obj):
        row_dict = doto.model.unwrap_obj(obj, ignore_list=['span', 'task'])
        row_dict['task_id'] = obj.task.id if obj.task is not None else None
        row_dict['start'] = obj.span.start
        row_dict['end'] = obj.span.end
        return row_dict


def get_started_timerecords(store):
    """
    Get all task which are not completed.

    @param cache if True the result will be stored in the cache
            so a cache_id can be used. Default=False
    @param limit Set the maximum number of returned items. Default=10

    @return A list of unfinished tasks
    """
    return store.query(Timerecord.row_to_obj, 'SELECT * FROM timerecords WHERE end IS NULL;', ())


insert_query = """INSERT INTO timerecords ( task_id,  start,  end)
                              VALUES      (:task_id, :start, :end)
                  ;
               """
update_query = """UPDATE timerecords SET task_id = :task_id,
                                         start = :start,
                                         end = :end
                                         WHERE id = :id;
               """
delete_query = 'DELETE FROM timerecords WHERE id = ?;'

update = doto.model.crud.update(update_query, Timerecord)
add_new = doto.model.crud.insert(insert_query, Timerecord)
delete = doto.model.crud.delete(delete_query)

doto.model.setup_module(CREATE_CMD, ())

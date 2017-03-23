import doto.model
import doto.model.crud


CREATE_CMD = '''
                CREATE TABLE IF NOT EXISTS
                    appointments (
                            id INTEGER NOT NULL,
                            title VARCHAR NOT NULL,
                            description VARCHAR,
                            created TIMESTAMP NOT NULL,
                            start TIMESTAMP NOT NULL,
                            end TIMESTAMP,
                            PRIMARY KEY (id)
                    );
             '''


class Appointment(doto.model.Event):
    """
    An appointment (APMT) has a fixed starting date and cannot be started or finished.

    """

    __tablename__ = "appointments"

    def __init__(self, title, start,
                 description=None, end=None
                 ):
        super().__init__(title, description)
        self.schedule = doto.model.TimeSpan(start, end)

    @staticmethod
    def row_to_obj(row, _store):
        '''
        Create Task from database row
        '''
        apmt = Appointment(row['title'],
                           row['start'],
                           row['description'],
                           row['end'],)
        apmt.id = row['id']
        apmt.created = row['created']
        return apmt

    @staticmethod
    def obj_to_row(obj):
        row_dict = doto.model.unwrap_obj(obj, ignore_list=['schedule'])
        row_dict['start'] = obj.schedule.start
        row_dict['end'] = obj.schedule.end
        return row_dict

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


def get_current(store, date, delta):
    """
    Get the appointments that are between the given date and the date + delta.

    So to get the appointments of the next seven days set date to now and delta to seven days.

    @param date The returned appointments are younger then this date.
    @param delta Only Appointments that are older than date + delta are returned.

    @return the appointments between the date and date + delta
    """
    query = 'SELECT * FROM appointments WHERE start >= :from AND start < :until;'

    apmts = store.query(Appointment.row_to_obj, query, {'from': date, 'until': date + delta})
    return apmts


def get_count(store):
    ''' Get the count Tasks in the database. '''
    def tuple_to_count(row, _store):
        (count,) = row
        return count
    return store.get_one(tuple_to_count, 'SELECT COUNT(id) FROM appointments')


insert_query = '''INSERT INTO appointments ( title,  description,  created,  start,  end)
                                    VALUES (:title, :description, :created, :start, :end)
                  ;
               '''
update_query = '''UPDATE appointments SET title = :title,
                                          description = :description,
                                          created = :created,
                                          start = :start,
                                          end = :end
                                         WHERE id = :id;
               '''
delete_query = 'DELETE FROM appointments WHERE id = ?;'
update = doto.model.crud.update(update_query, Appointment)
add_new = doto.model.crud.insert(insert_query, Appointment)
delete = doto.model.crud.delete(delete_query)


doto.model.setup_module(CREATE_CMD, ())

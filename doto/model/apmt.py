import doto.model
import doto.model.crud
import doto.model.repeat


CREATE_CMD = """
                CREATE TABLE IF NOT EXISTS
                    appointments (
                            id INTEGER NOT NULL,
                            title VARCHAR NOT NULL,
                            description VARCHAR,
                            created TIMESTAMP NOT NULL,
                            start TIMESTAMP NOT NULL,
                            end TIMESTAMP,
                            repeat INTEGER,
                            PRIMARY KEY (id),
                            FOREIGN KEY(repeat) REFERENCES repeats(id)
                    );
             """


class Appointment(doto.model.Event):
    """
    An appointment (APMT) has a fixed starting date and cannot be started or finished.

    """

    __tablename__ = "appointments"

    def __init__(self, title, start,
                 description=None, end=None,
                 repeat=None
                 ):
        super().__init__(title, description)
        self.schedule = doto.model.TimeSpan(start, end)
        self.repeat = repeat

    @staticmethod
    def row_to_obj(row, store):
        """
        Create Task from database row
        """
        apmt = doto.model.unwrap_row(store,
                                     row,
                                     Appointment,
                                     ('title', 'start', 'description', 'end'),
                                     ('id', 'created'),
                                     foreign_keys=(('repeat', doto.model.repeat),)
                                     )
        return apmt

    @staticmethod
    def obj_to_row(obj):
        """
        """
        row_dict = doto.model.unwrap_obj(obj, ignore_list=('schedule',), foreign_keys=('repeat',))
        row_dict['start'] = obj.schedule.start
        row_dict['end'] = obj.schedule.end
        row_dict['repeat'] = doto.model.get_id(obj.repeat)
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
        return ("%s(id=%s, title=%r, description=%r, start=%r, end=%r)" %
                (self.__class__.__name__,
                 self.id,
                 self.title,
                 self.description,
                 self.schedule.start,
                 self.schedule.end
                 )
                )


def create_repeat(store, apmt):
    """ Create a repeated appointment """
    next_dt = apmt.repeat.next(doto.model.now_with_tz())
    repeat = apmt.repeat
    apmt.schedule = doto.model.TimeSpan.move(apmt.schedule, next_dt)
    # TODO: This cries for a transaction
    new_apmt = add_new(store, apmt).id
    repeat.event = new_apmt
    doto.model.repeat.update(store, repeat)
    return new_apmt


def create_repeats(store):
    oudated_query = """SELECT appointments.* FROM appointments
                                               INNER JOIN repeats
                                               ON appointments.id=repeats.event
                                               WHERE appointments.start <= :now;
                      """
    outdated_apmts = store.query(Appointment.row_to_obj, oudated_query, {'now': doto.model.now_with_tz()})
    for apmt in outdated_apmts:
        create_repeat(store, apmt)


def get_many(store, query, params):
    create_repeats(store)
    return store.query(Appointment.row_to_obj, query, params)


def get_current(store, date, delta):
    """
    Get the appointments that are between the given date and the date + delta.

    So to get the appointments of the next seven days set date to now and delta to seven days.

    @param date The returned appointments are younger then this date.
    @param delta Only Appointments that are older than date + delta are returned.

    @return the appointments between the date and date + delta
    """
    query = 'SELECT * FROM appointments WHERE start >= :from AND start < :until ORDER BY start;'
    params = {'from': date, 'until': date + delta}

    return get_many(store, query, params)


def get_all(store, date):
    query = 'SELECT * FROM appointments WHERE start >= :from ORDER BY start;'
    params = {'from': date}
    return get_many(store, query, params)


count_query = 'SELECT COUNT(id) FROM appointments'
insert_query = """INSERT INTO appointments ( title,  description,  created,  start,  end,  repeat)
                                    VALUES (:title, :description, :created, :start, :end, :repeat)
                  ;
               """
update_query = """UPDATE appointments SET title = :title,
                                          description = :description,
                                          created = :created,
                                          start = :start,
                                          end = :end,
                                          repeat = :repeat
                                         WHERE id = :id;
               """
delete_query = 'DELETE FROM appointments WHERE id = ?;'
select_query = 'SELECT * FROM appointments WHERE id = :id;'
update = doto.model.crud.update(update_query, Appointment)
add_new = doto.model.crud.insert(insert_query, Appointment, add_fn=doto.model.crud.add_and_cache)
delete = doto.model.crud.delete(delete_query)
get = doto.model.crud.get(select_query, Appointment)
get_count = doto.model.crud.get_count(count_query)

doto.model.setup_module(CREATE_CMD, ())

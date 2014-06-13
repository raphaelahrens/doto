# -*- coding: utf-8 -*-
"""
The db module holds all classes and functions to handle the Database connection
and convert the data from the DB into the classes of the task module.
"""
import sqlite3
import os.path
import task

sqlite3.register_converter("DDate", task.Date.from_sqlite)
sqlite3.register_converter("TimeSpan", task.TimeSpan.from_sqlite)
sqlite3.register_converter("StateHolder", task.StateHolder.from_sqlite)


class DBException(Exception):
    """
    DBException is the Exception tht is thrown when an error
    occurs when handling the database connection
    """
    pass


class DBManager(object):
    """
    The DBManager handles the database connection and maps the database schema to the
    class hierarchy of Done!Tools.
    """

    @staticmethod
    def task_from_row(row):
        """
        Create a task from a row element

        @param row the row object that holds a task

        @returns the task that was crated rom the row object
        """
        schedule = task.Schedule(row["planned_sch"],
                                 row["real_sch"],
                                 due=row["due"])
        tsk = task.Task(title=row["title"],
                        description=row["description"],
                        difficulty=row["difficulty"],
                        category=row["category"],
                        )
        tsk.set_internals(row["state"], row["created"], schedule)
        tsk.event_id = row["task_id"]
        return tsk

    def __init__(self, db_name):
        create_tbls = not os.path.isfile(db_name)
        if db_name != ":memory:":
            DBManager.__create_dir(db_name)
        else:
            create_tbls = True
        self.__con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
        cursor = self.__con.cursor()
        # Since SQLite hadn't always had foreign keys it needs to be told it
        # has them now.
        cursor.execute('PRAGMA foreign_keys = ON;')
        self.__con.row_factory = sqlite3.Row
        if create_tbls:
            self.create_tables()

    @staticmethod
    def __create_dir(db_name):
        """
        Create the directory where the database file is store if the directories do not exist.

        @param db_name the name of the database file
        """
        import errno
        dir_path = os.path.dirname(db_name)
        try:
            os.makedirs(dir_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise DBException("The file " + db_name + " couldn't be created.")

    def create_tables(self):
        """ Create the database tables """
        with open("./db_schema.sql", "r") as schema_file:
            with self.__con:
                cur = self.__con.cursor()
                cur.executescript(schema_file.read())

    def get_tasks(self, cache, limit, only_undone=False):
        """
        Get tasks from the database

        @param cache if cache is True the result from this call will be stored in the cache
        @param limit Set the maximum limit of tasks that will be returned
        @param only_undone If True the method return only taks that are undone
        @param

        """
        if only_undone:
            select_str = "SELECT * FROM tasks WHERE state IS NOT \"" + task.StateHolder.completed.key + "\" LIMIT ?;"
        else:
            select_str = "SELECT * FROM tasks LIMIT ?;"
        with self.__con:
            cur = self.__con.cursor()
            cur.execute(select_str, (limit,))
            rows = cur.fetchall()
            tasks = [DBManager.task_from_row(row) for row in rows]
            if cache:
                # clear the task cache
                cur.execute("DELETE FROM task_cache;")
                cur.executemany("INSERT INTO task_cache VALUES (?,?);",
                                ((i, tsk.event_id) for i, tsk in zip(range(len(tasks)), tasks)))
            return tasks

    def get_cache(self):
        """
        Get the content of the cache.
        """
        select_str = "SELECT * FROM task_cache NATURAL JOIN tasks;"
        cur = self.__con.cursor()
        cur.execute(select_str)
        rows = cur.fetchall()

        return {row["cache_id"]: DBManager.task_from_row(row) for row in rows}

    def save_new(self, events):
        """
        Save the events in the DB.

        @param events the new events that will be stored in the database.
        """
        with self.__con:
            cur = self.__con.cursor()
            for event in events:
                (event.get_handler().save_new)(cur, event)
            return True
        return False

    def update(self, events):
        """
        Update the given events in the DB.

        @param events the events that will be updated

        """
        with self.__con:
            cur = self.__con.cursor()
            for event in events:
                event.get_handler().update(cur, event)
            return True
        return False

    def delete(self, events):
        """
        Delete the given events.

        @param events the events that will be deleted

        """
        delete_events = 0
        with self.__con:
            cur = self.__con.cursor()
            for event in events:
                delete_events += event.get_handler().delete(cur, event)
            return delete_events == len(events)
        return False

    def close(self):
        """
        Close the database connection.
        """
        self.__con.close()


def task_delete(cur, tsk):
    """
    Delete the given task in the task table

    @param cur cursor object for the db connection
    @param tsk the task that will be deleted

    """
    if tsk.event_id is None:
        return 0
    delete_task_str = "DELETE FROM tasks WHERE task_id = ?;"
    print str(tsk.event_id)
    cur.execute(delete_task_str, (tsk.event_id,))
    return cur.rowcount


def task_update(cur, tsk):
    """
    Update the given task in the task table

    @param cur cursor object for the db connection
    @param tsk the task that was updated

    """
    updatate_str = """UPDATE tasks SET
    title=?, description=?, state=?, difficulty=?, category=?,
    source=?, due=?, created=?, planned_sch=?, real_sch=?
    WHERE task_id=?;
    """
    cur.execute(updatate_str,
                (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                 None, tsk.schedule.due, tsk.created, tsk.schedule.planned, tsk.schedule.real, tsk.event_id
                 )
                )


def task_save_new(cur, tsk):
    """
    Save a new task in the tasks table

    @param cur cursor object for the db connection
    @param tsk the new task

    """
    insert_str = "INSERT INTO tasks VALUES(NULL,?,?,?,?,?,?,?,?,?,?);"
    cur.execute(insert_str,
                (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                 None, tsk.schedule.due, tsk.created, tsk.schedule.planned, tsk.schedule.real
                 )
                )
    tsk.event_id = cur.lastrowid


def apmt_delete(cur, apmt):
    """
    Delete the given appointment in the appointments table.

    @param cur cursor object for the db connection
    @param apmt the updated appointment

    @returns the number of changed rows in appointments

    """
    if apmt.apmt_id is None:
        return 0
    delete_task_str = "DELETE FROM appointments WHERE apmt_id = ?;"
    cur.execute(delete_task_str, (apmt.event_id,))
    return cur.rowcount


def apmt_update(cur, apmt):
    """
    Update the given appointment in the appointments table.

    @param cur cursor object for the db connection
    @param apmt the updated appointment

    """
    updatate_str = """UPDATE appointments SET
    title=?, description=?,
    created=?, schedule=?
    WHERE apmt_id=?;
    """
    cur.execute(updatate_str,
                (apmt.title, apmt.description, apmt.created,
                 apmt.schedule, apmt.event_id
                 )
                )


def apmt_save_new(cur, apmt):
    """
    Save the appointmen inside the appointments table.

    @param cur cursor object for the db connection
    @param apmt the new appointment
    """
    insert_str = "INSERT INTO appointments VALUES(NULL,?,?,?,?);"
    cur.execute(insert_str,
                (apmt.title, apmt.description,
                 apmt.schedule, apmt.created
                 )
                )
    apmt.apmt_id = cur.lastrowid


class Handler(object):
    """
    A dummy class to hold the handler functions.
    """
    pass


def init_handlers():
    """
    Set all handler for all the events that can be stored.
    """
    apmt_handler = Handler()
    apmt_handler.delete = apmt_delete
    apmt_handler.update = apmt_update
    apmt_handler.save_new = apmt_save_new
    task.Appointment.set_handler(apmt_handler)
    task_handler = Handler()
    task_handler.delete = task_delete
    task_handler.update = task_update
    task_handler.save_new = task_save_new
    task.Task.set_handler(task_handler)


init_handlers()

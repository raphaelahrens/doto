# -*- coding: utf-8 -*-
import sqlite3
import os.path
import task

sqlite3.register_converter("DDate", task.Date.from_sqlite)
sqlite3.register_converter("TimeSpan", task.TimeSpan.from_sqlite)
sqlite3.register_converter("StateHolder", task.StateHolder.from_sqlite)


class DBException(Exception):
    pass


class DBStore(object):

    @staticmethod
    def task_from_row(row):
        return task.Task(task_id=row["id"],
                         title=row["title"],
                         description=row["description"],
                         state=row["state"],
                         difficulty=row["difficulty"],
                         category=row["category"],
                         source=row["source"],
                         due=row["due"],
                         created=row["created"],
                         scheduled=row["scheduled"],
                         real_schedule=row["real"]
                         )

    def __init__(self, db_name):
        create_tbls = not os.path.isfile(db_name)
        if db_name != ":memory:":
            self.__create_dir(db_name)
        else:
            create_tbls = True
        self.__con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
        self.__con.row_factory = sqlite3.Row
        if create_tbls:
            self.create_tables()

    def __create_dir(self, db_name):
        import errno
        dir_path = os.path.dirname(db_name)
        try:
            os.makedirs(dir_path)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                raise DBException("The file " + db_name + " couldn't be created.")

    def create_tables(self):
        fd = open("./db_schema.sql", "r")
        with self.__con:
            cur = self.__con.cursor()
            cur.executescript(fd.read())
            cur.close()
        fd.close()

    def get_tasks(self):
        select_str = "SELECT * FROM tasks;"
        cur = self.__con.cursor()
        cur.execute(select_str)
        rows = cur.fetchall()
        cur.close()
        tasks = [DBStore.task_from_row(row) for row in rows]
        return tasks

    def save_new(self, tsk):
        insert_str = "INSERT INTO tasks VALUES(NULL,?,?,?,?,?,?,?,?,?,?);"
        with self.__con:
            cur = self.__con.cursor()
            cur.execute(insert_str,
                        (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                         None, tsk.due, tsk.created, tsk.scheduled, tsk.real_schedule)
                        )
            tsk.task_id = cur.lastrowid
            cur.close()
            return True
        return False

    def update(self, tsk):
        updatate_str = """UPDATE tasks SET
        title=?, description=?, state=?, difficulty=?, category=?,
        source=?, due=?, created=?, scheduled=?, real=?
        WHERE id=?;
        """
        with self.__con:
            cur = self.__con.cursor()
            cur.execute(updatate_str,
                        (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                         None, tsk.due, tsk.created, tsk.scheduled, tsk.real_schedule, tsk.task_id)
                        )
            cur.close()
            return True
        return False

    def delete(self, tsk):
        delete_str = "DELETE FROM tasks WHERE id = ?;"
        if tsk.task_id is None:
            return False
        with self.__con:
            cur = self.__con.cursor()
            cur.execute(delete_str, (tsk.task_id,))
            cur.close()
            return cur.rowcount == 1
        return False

    def close(self):
        self.__con.close()

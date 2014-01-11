import sqlite3
import task

sqlite3.register_converter("DDate", task.Date.from_sqlite)
sqlite3.register_converter("TimeSpan", task.TimeSpan.from_sqlite)
sqlite3.register_converter("StateHolder", task.StateHolder.from_sqlite)


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

    def __init__(self, db_name, create=False):
        self.__con = sqlite3.connect(db_name, detect_types=sqlite3.PARSE_DECLTYPES)
        self.__con.row_factory = sqlite3.Row
        if create:
            self.create()

    def create(self):
        fd = open("./db_schema.sql", "r")
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

    def store_new(self, tsk):
        insert_str = "INSERT INTO tasks VALUES(NULL,?,?,?,?,?,?,?,?,?,?);"
        cur = self.__con.cursor()
        cur.execute(insert_str,
                    (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                     None, tsk.due, tsk.created, tsk.scheduled, tsk.real_schedule)
                    )
        tsk.task_id = cur.lastrowid
        cur.close()

    def update(self, tsk):
        updatate_str = """UPDATE tasks SET
        title=?, description=?, state=?, difficulty=?, category=?,
        source=?, due=?, created=?, scheduled=?, real=?
        WHERE id=?;
        """
        cur = self.__con.cursor()
        cur.execute(updatate_str,
                    (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                     None, tsk.due, tsk.created, tsk.scheduled, tsk.real_schedule, tsk.task_id)
                    )
        cur.close()

    def delete(self, tsk):
        if not tsk.task_id:
            return False
        cur = self.__con.cursor()
        cur.execute("DELETE FROM tasks WHERE id = ?", (tsk.task_id,))
        cur.close()
        return cur.rowcount == 1

    def close(self):
        self.__con.close()


def create_tables(db_file):
    print ("""INSERT INTO tasks VALUES (Null, "Title", "Description", "STATE", 3, 4, 5, ?, ?, "TIME_SPAN", "TIME_SPAN2"); """, (task.Date.now(), task.Date.now()))
    print ("SELECT * FROM tasks;")

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
        cur = self.__con.cursor()
        cur.execute("SELECT * FROM tasks;")
        rows = cur.fetchall()
        cur.close()
        tasks = [DBStore.task_from_row(row) for row in rows]
        return tasks

    def add(self, tsk):
        cur = self.__con.cursor()
        cur.execute("INSERT INTO tasks VALUES(NULL,?,?,?,?,?,?,?,?,?,?);",
                    (tsk.title, tsk.description, tsk.state, tsk.difficulty, tsk.category,
                     0, tsk.due, tsk.created, tsk.scheduled, tsk.real_schedule)
                    )
        cur.close()

    def update(self, task):
        pass

    def remove(self, task):
        pass

    def close(self):
        self.__con.close()


def create_tables(db_file):
    print ("""INSERT INTO tasks VALUES (Null, "Title", "Description", "STATE", 3, 4, 5, ?, ?, "TIME_SPAN", "TIME_SPAN2"); """, (task.Date.now(), task.Date.now()))
    print ("SELECT * FROM tasks;")

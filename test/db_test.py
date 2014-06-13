""" Tests for the DBManager """
import unittest
import shutil
import os.path
import tempfile

import db
import task

TEST_DB_FILE = ":memory:"


class TestDBManager(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def setUp(self):
        """ Create a new Db store. """
        self.db_store = db.DBManager(TEST_DB_FILE)

    def tearDown(self):
        """ Close the connection after everx test. """
        self.db_store.close()

    def test_init(self):
        """ Test the constructor of the database store. """
        tasks = self.db_store.get_tasks(False, 10)
        self.assertEqual(tasks, [])

    def test_store(self):
        """ Test if we can store tasks. """
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        tasks = self.db_store.get_tasks(False, 10)
        self.assertEqual(tasks, [test_task])

    def test_get_tasks_with_undone_only(self):
        """ Test if we can get only unfinished tasks. """
        test_done = task.Task("title", "description")
        test_done.done()
        test_open = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_done, test_open]))
        tasks = self.db_store.get_tasks(False, 10, True)
        self.assertEqual(tasks, [test_open])

    def test_get_tasks_with_cache(self):
        """ Test if we can gte a list of the tasks and also create the cache. """
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        tasks = self.db_store.get_tasks(True, 10)
        self.assertEqual(tasks, [test_task])
        cache = self.db_store.get_cache()
        self.assertTrue(len(cache) > 0)
        self.assertEqual(cache, {i: tsk for i, tsk in zip(range(len(tasks)), tasks)})

    def test_store_10(self):
        """ Test if we can save 10 tasks in a row. """
        test_task = task.Task("title", "description")
        ref_list = []
        for _ in range(10):
            self.db_store.save_new([test_task])
            ref_list.append(test_task)
        tasks = self.db_store.get_tasks(False, 10)
        self.assertEqual(tasks, ref_list)

    def test_update(self):
        """ Test if we can update Tasks in the store. """
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        test_task2 = task.Task(title="newTitle", description="new description")
        test_task2.event_id = test_task.event_id
        test_task2.schedule.due = task.Date.now()
        self.assertTrue(self.db_store.update([test_task2]))
        tasks = self.db_store.get_tasks(False, 10)
        self.assertEqual(tasks, [test_task2])

    def test_delete(self):
        """ Test if we can delete tasks from the store. """
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        self.assertTrue(self.db_store.delete([test_task]))
        tasks = self.db_store.get_tasks(False, 10)
        self.assertEqual(tasks, [])

    def test_fail_delete(self):
        """ Test if a task with no id can't be deleted. """
        test_task = task.Task("title", "description")
        self.assertFalse(self.db_store.delete([test_task]))


class TestDBFiles(unittest.TestCase):
    """ Tests for creating store files. """

    @classmethod
    def setUpClass(cls):
        """ Set up the test path and base in /tmp """
        cls.base = tempfile.mkdtemp() + "/"
        cls.path = cls.base + "./test/db/test123/"

    def test_create_store(self):
        """ Test if we can create a new store file """
        test_file = self.path + "file1.db"
        self.db_store = db.DBManager(test_file)
        self.db_store.close()
        self.assertTrue(os.path.isfile(test_file))

    def test_create_and_read(self):
        """ Test if we can create a new  """
        test_file = self.path + "file2.db"
        test_task = task.Task("create a file and read it", "We want a new db file and read this task from it.")
        self.db_store = db.DBManager(test_file)
        self.db_store.save_new([test_task])
        self.assertEqual(self.db_store.get_tasks(False, 10), [test_task])
        self.db_store.close()
        self.assertTrue(os.path.isfile(test_file))
        self.db_store = db.DBManager(test_file)
        self.assertEqual(self.db_store.get_tasks(False, 10), [test_task])
        self.db_store.close()

    @classmethod
    def tearDownClass(cls):
        """ Clear up the directory we created """
        shutil.rmtree(cls.base)

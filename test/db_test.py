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
        self.db_store = db.DBManager(TEST_DB_FILE)

    def tearDown(self):
        self.db_store.close()

    def test_init(self):
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_store(self):
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [test_task])

    def test_store_10(self):
        test_task = task.Task("title", "description")
        ref_list = []
        for _ in range(10):
            self.db_store.save_new([test_task])
            ref_list.append(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, ref_list)

    def test_update(self):
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        print test_task.task_id
        test_task2 = task.Task(task_id=test_task.task_id, title="newTitle", description="new description")
        test_task2.schedule.due = task.Date.now()
        self.assertTrue(self.db_store.update([test_task2]))
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [test_task2])

    def test_delete(self):
        test_task = task.Task("title", "description")
        self.assertTrue(self.db_store.save_new([test_task]))
        self.assertTrue(self.db_store.delete([test_task]))
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_fail_delete(self):
        test_task = task.Task("title", "description")
        self.assertFalse(self.db_store.delete([test_task]))


class TestDBFiles(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base = tempfile.mkdtemp() + "/"
        cls.path = cls.base + "./test/db/test123/"

    def test_create_store(self):
        test_file = self.path + "file1.db"
        self.db_store = db.DBManager(test_file)
        self.db_store.close()
        self.assertTrue(os.path.isfile(test_file))

    def test_create_and_read(self):
        test_file = self.path + "file2.db"
        test_task = task.Task("create a file and read it", "We want a new db file and read this task from it.")
        self.db_store = db.DBManager(test_file)
        self.db_store.save_new([test_task])
        self.assertEqual(self.db_store.get_tasks(), [test_task])
        self.db_store.close()
        self.assertTrue(os.path.isfile(test_file))
        self.db_store = db.DBManager(test_file)
        self.assertEqual(self.db_store.get_tasks(), [test_task])
        self.db_store.close()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.base)

import unittest

import db
import task

TEST_DB_FILE = ":memory:"


class TestDBStore(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def setUp(self):
        self.db_store = db.DBStore(TEST_DB_FILE, create=True)

    def tearDown(self):
        self.db_store.close()

    def test_init(self):
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_store(self):
        test_task = task.Task("title", "description")
        self.db_store.store_new(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [test_task])

    def test_store_10(self):
        test_task = task.Task("title", "description")
        ref_list = []
        for _ in range(10):
            self.db_store.store_new(test_task)
            ref_list.append(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, ref_list)

    def test_update(self):
        test_task = task.Task("title", "description")
        self.db_store.store_new(test_task)
        print test_task.task_id
        test_task2 = task.Task(task_id=test_task.task_id, title="newTitle", description="new description", due=task.Date.now())
        self.db_store.update(test_task2)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [test_task2])

    def test_delete(self):
        test_task = task.Task("title", "description")
        self.db_store.store_new(test_task)
        self.assertTrue(self.db_store.delete(test_task))
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_fail_delete(self):
        test_task = task.Task("title", "description")
        self.assertFalse(self.db_store.delete(test_task))

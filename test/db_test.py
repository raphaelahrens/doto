import unittest

import db
import task


class TestDBStore(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def setUp(self):
        self.db_store = db.DBStore("./test/data/test.db", create=True)

    def tearDown(self):
        self.db_store.close()

    def test_init(self):
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_multiple_inits(self):
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])
        self.db_store.close()
        self.db_store = db.DBStore("./test/data/test.db")
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_add(self):
        test_task = task.Task("title", "description")
        self.db_store.add(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [test_task])

    def test_add_100(self):
        test_task = task.Task("title", "description")
        ref_list = []
        for _ in range(10):
            self.db_store.add(test_task)
            ref_list.append(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, ref_list)

    def test_update(self):
        test_task = task.Task("title", "description")
        self.db_store.add(test_task)
        test_task.title = "new Title"
        self.db_store.update(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [test_task])

    def test_remove(self):
        test_task = task.Task("title", "description")
        self.db_store.add(test_task)
        self.db_store.remove(test_task)
        tasks = self.db_store.get_tasks()
        self.assertEqual(tasks, [])

    def test_fail_remove(self):
        test_task = task.Task("title", "description")
        self.assertRaises(Exception, self.db_store.remove, (test_task))

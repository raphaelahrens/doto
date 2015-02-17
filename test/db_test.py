""" Tests for the DBManager """
import unittest
import shutil
import os.path
import tempfile

import dbmodel
import datetime
import pytz

TEST_DB_FILE = ""
TEST_CAHCE_FILE = "./test/store/cache"


class TestDBManager(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def setUp(self):
        """ Create a new Db store. """
        self.store = dbmodel.Store(TEST_DB_FILE, TEST_CAHCE_FILE)

    def tearDown(self):
        """ Close the connection after everx test. """
        self.store.close()

    def test_init(self):
        """ Test the constructor of the database store. """
        tasks = self.store.get_tasks(10)
        self.assertEqual(tasks, [])

    def test_store(self):
        """ Test if we can store tasks. """
        test_task = dbmodel.Task("title", "description")
        self.store.add_new(test_task)
        self.store.save()
        tasks = self.store.get_tasks(10)
        self.assertEqual(tasks, [test_task])

    def test_get_tasks_with_undone_only(self):
        """ Test if we can get only unfinished tasks. """
        test_done = dbmodel.Task("title", "description")
        test_done.done()
        test_open = dbmodel.Task("title", "description")
        self.store.add_new([test_done, test_open])
        self.store.save()
        tasks = self.store.get_open_tasks(10)
        self.assertEqual(tasks, [test_open])

    def test_get_tasks_with_cache(self):
        """ Test if we can gte a list of the tasks and also create the cache. """
        self.store.enable_caching()
        test_task = dbmodel.Task("title", "description")
        self.store.add_new(test_task)
        tasks = self.store.get_tasks(10)
        self.assertEqual(tasks, [test_task])
        cache = self.store.get_cache()
        self.assertTrue(len(cache) > 0)
        # self.assertEqual(cache, {i: tsk for i, tsk in zip(range(len(tasks)), tasks)})

    def test_store_10(self):
        """ Test if we can save 10 tasks in a row. """
        ref_list = [dbmodel.Task("title %i" % i, "description") for i in xrange(10)]
        self.store.add_new(ref_list)
        self.store.save()
        tasks = self.store.get_tasks(10)
        self.assertEqual(tasks, ref_list)

    def test_update(self):
        """ Test if we can update Tasks in the store. """
        test_task = dbmodel.Task("title", "description")
        self.store.add_new(test_task)
        self.store.save()
        self.assertTrue(self.store.is_saved)
        now = datetime.datetime.now(tz=pytz.utc)
        test_task.due = now
        self.assertFalse(self.store.is_saved)
        self.store.save()
        tasks = self.store.get_tasks(10)
        self.assertEqual(tasks, [test_task])
        self.assertEqual(tasks[0].due, now)

    def test_delete(self):
        """ Test if we can delete tasks from the store. """
        test_task = dbmodel.Task("title", "description")
        self.store.add_new([test_task])
        self.store.save()
        self.store.delete(test_task)
        self.store.save()
        tasks = self.store.get_tasks(10)
        self.assertEqual(tasks, [])

    def test_fail_delete(self):
        """ Test if a task with no id can't be deleted. """
        test_task = dbmodel.Task("title", "description")
        self.assertFalse(self.store.delete(test_task))
        self.store.save()


class TestDBFiles(unittest.TestCase):
    """ Tests for creating store files. """

    @classmethod
    def setUpClass(cls):
        """ Set up the test path and base in /tmp """
        cls.base = tempfile.mkdtemp()
        cls.path = os.path.join(cls.base, "test/db/test123/")

    def test_create_store(self):
        """ Test if we can create a new store file """
        test_file = os.path.join(self.path, "file1.db")
        self.store = dbmodel.Store(test_file, TEST_CAHCE_FILE)
        self.store.close()
        self.assertTrue(os.path.isfile(test_file))

    def test_create_and_read(self):
        """ Test if we can create a new  """
        test_file = os.path.join(self.path, "file2.db")
        test_task = dbmodel.Task("create a file and read it", "We want a new db file and read this task from it.")
        self.store = dbmodel.Store(test_file, TEST_CAHCE_FILE)
        self.store.add_new(test_task)
        self.store.save()
        self.assertEqual(self.store.get_tasks(10), [test_task])
        self.store.close()
        self.assertTrue(os.path.isfile(test_file))
        self.store = dbmodel.Store(test_file, TEST_CAHCE_FILE)
        self.assertEqual(self.store.get_tasks(10), [test_task])
        self.store.close()

    @classmethod
    def tearDownClass(cls):
        """ Clear up the directory we created """
        shutil.rmtree(cls.base)

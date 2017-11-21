""" Tests for the DBManager """
import unittest
import shutil
import os.path
import tempfile

import doto.model
import doto.model.timerecord
import doto.model.task
import doto.model.apmt
import doto.model.repeat

TEST_DB_FILE = ""
TEST_CACHE_FILE = "./test/store/cache"
TEST_LAST_FILE = "./test/store/last"


class TestDBManager(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def setUp(self):
        """ Create a new Db store. """
        self.store = doto.model.Store(TEST_DB_FILE, TEST_CACHE_FILE, TEST_LAST_FILE)

    def tearDown(self):
        """ Close the connection after everx test. """
        self.store.close()

    def test_init(self):
        """ Test the constructor of the database store. """
        tasks = doto.model.task.get_many(self.store, 10)
        self.assertListEqual(tasks, [])

    def test_store(self):
        """ Test if we can store tasks. """
        test_task = doto.model.task.Task("title", "description")
        doto.model.task.add_new(self.store, test_task)
        self.store.save()
        tasks = doto.model.task.get_many(self.store, 10)
        self.assertListEqual(tasks, [test_task])

    def test_get_tasks_with_undone_only(self):
        """ Test if we can get only unfinished tasks. """
        test_done = doto.model.task.Task("title", "description")
        test_done.done()
        test_open = doto.model.task.Task("title", "description")
        doto.model.task.add_new(self.store, test_done)
        doto.model.task.add_new(self.store, test_open)
        self.store.save()
        tasks = doto.model.task.get_open_tasks(self.store, 10)
        self.assertListEqual(tasks, [test_open])

    def test_get_tasks_with_cache(self):
        """ Test if we can get a list of the tasks and also create the cache. """
        test_task = doto.model.task.Task("title", "description")
        doto.model.task.add_new(self.store, test_task)
        tasks = doto.model.task.get_many(self.store, 10)
        self.assertListEqual(tasks, [test_task])
        cache = self.store.get_cache()
        self.assertTrue(len(cache) > 0)
        # self.assertEqual(cache, {i: tsk for i, tsk in zip(range(len(tasks)), tasks)})

    def test_store_10(self):
        """ Test if we can save 10 tasks in a row. """
        ref_list = [doto.model.task.Task("title %i" % i, "description") for i in range(10)]
        doto.model.task.add_new(self.store, ref_list)
        self.store.save()
        tasks = doto.model.task.get_many(self.store, 10)
        self.assertListEqual(tasks, ref_list)

    def test_update(self):
        """ Test if we can update Tasks in the store. """
        test_task = doto.model.task.Task("title", "description")
        doto.model.task.add_new(self.store, test_task)
        self.store.save()
        now = doto.model.now_with_tz()
        test_task.due = now
        doto.model.task.update(self.store, test_task)
        self.store.save()
        tasks = doto.model.task.get_many(self.store, 10)
        self.assertListEqual(tasks, [test_task])
        self.assertEqual(tasks[0].due, now)

    def test_delete(self):
        """ Test if we can delete tasks from the store. """
        test_task = doto.model.task.Task("title", "description")
        doto.model.task.add_new(self.store, [test_task])
        self.store.save()
        doto.model.task.delete(self.store, test_task)
        self.store.save()
        tasks = doto.model.task.get_many(self.store, 10)
        self.assertListEqual(tasks, [])

    def test_repeat(self):
        ''' Test if we can create a repeat object. '''
        task = doto.model.task.Task("title", "description")
        self.store.save()
        doto.model.task.add_new(self.store, task)
        repeat = doto.model.repeat.parse('@yearly', doto.model.now_with_tz(), event=task.id)
        doto.model.repeat.add_new(self.store, repeat)
        self.store.save()
        repeat_two = doto.model.repeat.get(self.store, repeat.id)
        self.assertEqual(repeat_two, repeat)

    def test_fail_delete(self):
        """ Test if a task with no id can't be deleted. """
        test_task = doto.model.task.Task("title", "description")
        self.assertFalse(doto.model.task.delete(self.store, test_task))
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
        store = doto.model.Store(test_file, TEST_CACHE_FILE, TEST_LAST_FILE)
        store.close()
        self.assertTrue(os.path.isfile(test_file))

    def test_create_and_read(self):
        """ Test if we can create a new  """
        test_file = os.path.join(self.path, "file2.db")
        test_task = doto.model.task.Task("create a file and read it",
                                         "We want a new db file and read this task from it.")
        store = doto.model.Store(test_file, TEST_CACHE_FILE, TEST_LAST_FILE)
        doto.model.task.add_new(store, test_task)
        store.save()
        self.assertListEqual(doto.model.task.get_open_tasks(store, 10), [test_task])
        store.close()
        self.assertTrue(os.path.isfile(test_file))
        store = doto.model.Store(test_file, TEST_CACHE_FILE, TEST_LAST_FILE)
        self.assertListEqual(doto.model.task.get_open_tasks(store, 10), [test_task])
        store.close()

    @classmethod
    def tearDownClass(cls):
        """ Clear up the directory we created """
        shutil.rmtree(cls.base)

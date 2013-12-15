"""Unitests for the task module."""

import unittest
import task
from datetime import datetime, timedelta
import pytz

title = "important task"
description = "long description of this task \n"


class TestDate(unittest.TestCase):

    """Unittest for the Date class."""

    @classmethod
    def setUpClass(cls):
        """ Setup of datetime object for comparisons."""
        cls.d1 = datetime(2011, 12, 13, 14, 15, 16, tzinfo=task.Date.local_tz)
        cls.d2 = cls.d1.astimezone(pytz.utc)
        cls.d_gt = datetime(2012, 12, 13, 14, 15, 16, tzinfo=task.Date.local_tz)
        cls.d_lt = datetime(2010, 12, 13, 14, 15, 16, tzinfo=task.Date.local_tz)

    def test_local_constructor(self):
        """Test the local constructor of Date."""
        local = task.Date.local(2011, 12, 13, 14, 15, 16)
        self.assertEqual(local, self.d1)
        self.assertEqual(local, self.d2)

    def test_eq(self):
        """."""
        local1 = task.Date.local(2011, 12, 13, 14, 15, 16)
        local2 = task.Date.local(2011, 12, 13, 14, 15, 16)
        self.assertEqual(local1, local2)
        self.assertEqual(local1, self.d1)
        self.assertEqual(local1, self.d2)

    def test_gt(self):
        """Test if the greater operator works."""
        big = task.Date.local(2012, 12, 13, 14, 15, 16)
        small = task.Date.local(2011, 12, 13, 14, 15, 16)
        self.assertGreater(big, small)
        self.assertGreater(big, self.d1)
        self.assertGreater(big, self.d2)

    def test_ge(self):
        """Test if the greater equal operator works."""
        big = task.Date.local(2012, 12, 13, 14, 15, 16)
        small = task.Date.local(2011, 12, 13, 14, 15, 16)
        equal = task.Date.local(2012, 12, 13, 14, 15, 16)
        self.assertGreaterEqual(big, small)
        self.assertGreaterEqual(big, equal)
        self.assertGreaterEqual(big, self.d1)
        self.assertGreaterEqual(big, self.d2)
        self.assertGreaterEqual(big, self.d_lt)

    def test_lt(self):
        """Test if the lesser operator works."""
        small = task.Date.local(2010, 12, 13, 14, 15, 16)
        big = task.Date.local(2012, 12, 13, 14, 15, 16)
        self.assertLess(small, big)
        self.assertLess(small, self.d1)
        self.assertLess(small, self.d2)

    def test_le(self):
        """Test if the lesser equal operator works."""
        small = task.Date.local(2010, 12, 13, 14, 15, 16)
        big = task.Date.local(2011, 12, 13, 14, 15, 16)
        equal = task.Date.local(2010, 12, 13, 14, 15, 16)
        self.assertLessEqual(small, big)
        self.assertLessEqual(small, equal)
        self.assertLessEqual(small, self.d1)
        self.assertLessEqual(small, self.d2)
        self.assertLessEqual(small, self.d_lt)

    def test_sub(self):
        """Test if the subtraction operator works."""
        a = task.Date.local(2010, 12, 13, 14, 15, 16)
        b = task.Date.local(2010, 12, 13, 14, 14, 16)
        delta = timedelta(0, 60, 0)
        self.assertEqual(a - b, delta)

    def test_add(self):
        """Test if the add operator works."""
        a = task.Date.local(2010, 12, 13, 14, 15, 16)
        b = timedelta(0, 60, 0)
        x = task.Date.local(2010, 12, 13, 14, 16, 16)
        self.assertEqual(x, a + b)


class TestTimeSpan(unittest.TestCase):

    """Unittest for the TimeSpan class."""

    @classmethod
    def setUpClass(cls):
        """Set up the test data, start and end (start < end)."""
        cls.start = task.Date.local(2011, 12, 13, 14, 15, 16)
        cls.end = task.Date.local(2011, 12, 14, 14, 15, 16)

    def test_constructor(self):
        """Test for the constructor of TimeSpan."""
        span = task.TimeSpan(start=self.start, end=self.end)
        self.assertEqual(span.start, self.start)
        self.assertEqual(span.end, self.end)

    def test_set_start(self):
        """Test the start setter."""
        span = task.TimeSpan()
        span.start = self.start
        self.assertEqual(span.start, self.start)

    def test_set_end(self):
        """Test the end setter."""
        span = task.TimeSpan()
        span.end = self.end
        self.assertEqual(span.end, self.end)

    def test_start_greater_end(self):
        """Test that start is greater then end."""
        span = task.TimeSpan()
        span.start = self.start
        span.end = self.end
        self.assertEqual(span.end, self.end)
        self.assertEqual(span.start, self.start)
        self.assertGreater(span.end, span.start)

    def test_start_end_equal(self):
        """Test if start and end can be set to be equal."""
        span = task.TimeSpan()
        span.start = self.start
        span.end = self.start
        self.assertEqual(span.end, self.start)
        self.assertEqual(span.start, self.start)
        self.assertEqual(span.end, span.start)

    def test_fail_on_end_lesser_start(self):
        """Test if the start setter fails if start > end."""
        span = task.TimeSpan()
        span.end = self.start
        with self.assertRaises(AssertionError):
            span.start = self.end

    def test_fail_on_start_greater_end(self):
        """Test if the end setter fails if start > end."""
        span = task.TimeSpan()
        span.start = self.end
        with self.assertRaises(AssertionError):
            span.end = self.start

    def test_fail_2_start_greater_end(self):
        """Test if the contructor fails if start > end."""
        with self.assertRaises(AssertionError):
            task.TimeSpan(self.end, self.start)


class TestState(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def test_contructor(self):
        """Test if the constructor works properly."""
        state = task.StateHolder()
        self.assertEqual(state.state, task.StateHolder.pending)

    def test_contructor2(self):
        """Test if the constructor works properly with arguments."""
        for v in task.StateHolder.states.itervalues():
            state = task.StateHolder(v)
            self.assertEqual(state.state, v)

    def test_next(self):
        """Test if the next_state method gives us the next state."""
        state = task.StateHolder()
        self.assertEqual(state.state, task.StateHolder.pending)
        actions = state.get_actions()
        state.next_state(action=actions[0])
        self.assertEqual(state.state, task.StateHolder.started)

    def test_multiple_next(self):
        """."""
        state = task.StateHolder(task.StateHolder.started)
        self.assertEqual(state.state, task.StateHolder.started)

        for _ in range(100):
            state.next_state("block")
            self.assertEqual(state.state, task.StateHolder.blocked)
            state.next_state("unblock")
            self.assertEqual(state.state, task.StateHolder.started)
            state.next_state("interrupt")
            self.assertEqual(state.state, task.StateHolder.interrupted)
            state.next_state("restart")
            self.assertEqual(state.state, task.StateHolder.started)

        state.next_state("complete")
        self.assertEqual(state.state, task.StateHolder.completed)

    def test_fail_on_final(self):
        """Test if next_state fail when called on a FinalState."""
        from state import FinalStateException
        state = task.StateHolder(task.StateHolder.completed)
        self.assertRaises(FinalStateException, state.next_state, ("test"))

    def test_fail_wrong_action(self):
        """Test if next_state fails on wrong input."""
        state = task.StateHolder(task.StateHolder.started)
        self.assertRaises(KeyError, state.next_state, "test")


class TestTask(unittest.TestCase):

    """Test for the Task class."""

    def test_constructor(self):
        """Test the constructor of the Task."""
        t = task.Task(title=title, description=description)
        self.assertEqual(t.title, title)
        self.assertEqual(t.description, description)


class TestStore(unittest.TestCase):

    """Test if the task storing and loading data with the task store"""

    path = "./test/data/"

    def test_load_empty(self):
        """Test if we can load the empty file data_load_empty.doto ."""
        store = task.Store(TestStore.path + "data_load_empty.doto")
        self.assertEquals(store._version, 9)
        self.assertEquals(store._tasks, [])

    def test_save_load_empty(self):
        """Test if it is possible to load the saved data."""
        store = task.Store(TestStore.path + "data_save.doto", create=True)
        store.save()
        self.assertTrue(store.saved)
        store = task.Store(TestStore.path + "data_save.doto")
        self.assertEqual(store._version, 0)
        self.assertEqual(store._tasks, [])

    def test_save_load_100(self):
        """Test if we ca store 100 tasks and restore them."""
        t = task.Task("title", "description")
        save_store = task.Store(TestStore.path + "data_save_100.doto", create=True)
        for i in range(100):
            save_store.add(t)
        save_store.save()
        self.assertTrue(save_store.saved)
        load_store = task.Store(TestStore.path + "data_save_100.doto")
        for i in range(100):
            self.assertEqual(load_store._tasks[i], t)
        self.assertEqual(load_store._version, 0)

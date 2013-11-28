import unittest

import task

from datetime import datetime, timedelta
import pytz

title = "important task"
description = "long description of this task \n"


class TestDate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.d1 = datetime(2011, 12, 13, 14, 15, 16, tzinfo=task.Date.local_tz)
        cls.d2 = cls.d1.astimezone(pytz.utc)
        cls.d_gt = datetime(2012, 12, 13, 14, 15, 16, tzinfo=task.Date.local_tz)
        cls.d_lt = datetime(2010, 12, 13, 14, 15, 16, tzinfo=task.Date.local_tz)

    def test_constructor(self):
        local = task.Date.local(2011, 12, 13, 14, 15, 16)
        self.assertEqual(local, self.d1)
        self.assertEqual(local, self.d2)

    def test_eq(self):
        local1 = task.Date.local(2011, 12, 13, 14, 15, 16)
        local2 = task.Date.local(2011, 12, 13, 14, 15, 16)
        self.assertEqual(local1, local2)
        self.assertEqual(local1, self.d1)
        self.assertEqual(local1, self.d2)

    def test_gt(self):
        big = task.Date.local(2012, 12, 13, 14, 15, 16)
        small = task.Date.local(2011, 12, 13, 14, 15, 16)
        self.assertGreater(big, small)
        self.assertGreater(big, self.d1)
        self.assertGreater(big, self.d2)

    def test_ge(self):
        big = task.Date.local(2012, 12, 13, 14, 15, 16)
        small = task.Date.local(2011, 12, 13, 14, 15, 16)
        equal = task.Date.local(2012, 12, 13, 14, 15, 16)
        self.assertGreaterEqual(big, small)
        self.assertGreaterEqual(big, equal)
        self.assertGreaterEqual(big, self.d1)
        self.assertGreaterEqual(big, self.d2)
        self.assertGreaterEqual(big, self.d_lt)

    def test_lt(self):
        small = task.Date.local(2010, 12, 13, 14, 15, 16)
        big = task.Date.local(2012, 12, 13, 14, 15, 16)
        self.assertLess(small, big)
        self.assertLess(small, self.d1)
        self.assertLess(small, self.d2)

    def test_le(self):
        small = task.Date.local(2010, 12, 13, 14, 15, 16)
        big = task.Date.local(2011, 12, 13, 14, 15, 16)
        equal = task.Date.local(2010, 12, 13, 14, 15, 16)
        self.assertLessEqual(small, big)
        self.assertLessEqual(small, equal)
        self.assertLessEqual(small, self.d1)
        self.assertLessEqual(small, self.d2)
        self.assertLessEqual(small, self.d_lt)

    def test_sub(self):
        a = task.Date.local(2010, 12, 13, 14, 15, 16)
        b = task.Date.local(2010, 12, 13, 14, 14, 16)
        delta = timedelta(0, 60, 0)
        self.assertEqual(a - b, delta)

    def test_add(self):
        a = task.Date.local(2010, 12, 13, 14, 15, 16)
        b = timedelta(0, 60, 0)
        x = task.Date.local(2010, 12, 13, 14, 16, 16)
        self.assertEqual(x, a + b)


class TestTimeSpan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start = task.Date.local(2011, 12, 13, 14, 15, 16)
        cls.end = task.Date.local(2011, 12, 14, 14, 15, 16)

    """
    Test for the TimeSpan class
    """
    def test_constructor(self):
        """
        Test for the constructor of TimeSpan
        """
        span = task.TimeSpan(start=self.start, end=self.end)
        self.assertEqual(span.start, self.start)
        self.assertEqual(span.end, self.end)

    def test_set_start(self):
        span = task.TimeSpan()
        span.start = self.start
        self.assertEqual(span.start, self.start)

    def test_set_end(self):
        span = task.TimeSpan()
        span.end = self.end
        self.assertEqual(span.end, self.end)

    def test_start_greater_end(self):
        span = task.TimeSpan()
        span.start = self.start
        span.end = self.end
        self.assertEqual(span.end, self.end)
        self.assertEqual(span.start, self.start)
        self.assertGreater(span.end, span.start)

    def test_start_end_equal(self):
        span = task.TimeSpan()
        span.start = self.start
        span.end = self.start
        self.assertEqual(span.end, self.start)
        self.assertEqual(span.start, self.start)
        self.assertEqual(span.end, span.start)

    def test_fail_on_start_greater_end(self):
        span = task.TimeSpan()
        span.start = self.end
        with self.assertRaises(AssertionError):
            span.end = self.start

    def test_fail_2_start_greater_end(self):
        with self.assertRaises(AssertionError):
            task.TimeSpan(self.end, self.start)


class TestState(unittest.TestCase):
    def test_contructor(self):
        """
        Test if the constructor works properly
        """
        state = task.TaskStateHolder()
        self.assertEqual(state._state, task.TaskStateHolder.pending)

    def test_contructor2(self):
        """
        Test if the constructor works properly
        """
        for k, v in task.TaskStateHolder.states.iteritems():
            state = task.TaskStateHolder(v)
            self.assertEqual(state._state, v)

    def test_next(self):
        state = task.TaskStateHolder()
        self.assertEqual(state._state, task.TaskStateHolder.pending)
        actions = state.get_actions()
        print actions
        state.next_state(action=actions[0])
        self.assertEqual(state._state, task.TaskStateHolder.started)


class TestTask(unittest.TestCase):
    """
    Test for the Task class
    """

    def test_constructor(self):
        """
        Test the constructor of the Task
        """
        t = task.Task(title=title, description=description)
        self.assertEqual(t.title, title)
        self.assertEqual(t.description, description)

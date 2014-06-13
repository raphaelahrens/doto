"""Unitests for the task module."""

import unittest
import task
from datetime import datetime, timedelta
import pytz
import sqlite3

TITLE = "important task"
DESCRIPTION = "long description of this task \n"


class TestDate(unittest.TestCase):

    """Unittest for the Date class."""

    @classmethod
    def setUpClass(cls):
        """ Setup of datetime object for comparisons."""
        cls.d1 = datetime(2011, 12, 13, 14, 15, tzinfo=task.Date._local_tz)
        cls.d2 = cls.d1.astimezone(pytz.utc)
        cls.d_gt = datetime(2012, 12, 13, 14, 15, 16, tzinfo=task.Date._local_tz)
        cls.d_lt = datetime(2010, 12, 13, 14, 15, 16, tzinfo=task.Date._local_tz)

    def test_local_constructor(self):
        """Test the local constructor of Date."""
        local = task.Date.local(2011, 12, 13, 14, 15)
        self.assertEqual(local, self.d1)
        self.assertEqual(local, self.d2)

    def test_local_constructor2(self):
        """Test the local constructor of Date."""
        local_str = self.d1.strftime(task.Date._local_input_str)
        local = task.Date.local_from_str(local_str)
        self.assertEqual(local, self.d1)
        self.assertEqual(local, self.d2)

    def test_eq(self):
        """."""
        local1 = task.Date.local(2011, 12, 13, 14, 15)
        local2 = task.Date.local(2011, 12, 13, 14, 15)
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
        date_a = task.Date.local(2010, 12, 13, 14, 15, 16)
        date_b = task.Date.local(2010, 12, 13, 14, 14, 16)
        delta = timedelta(0, 60, 0)
        self.assertEqual(date_a - date_b, delta)

    def test_add(self):
        """Test if the add operator works."""
        date_a = task.Date.local(2010, 12, 13, 14, 15, 16)
        delta_b = timedelta(0, 60, 0)
        date_x = task.Date.local(2010, 12, 13, 14, 16, 16)
        self.assertEqual(date_x, date_a + delta_b)

    def test_conform(self):
        """Test if it is possible to create and retrieve a Date Object."""
        d_org = task.Date.now()
        sql_str = d_org.__conform__(sqlite3.PrepareProtocol)
        d_copy = task.Date.from_sqlite(sql_str)
        self.assertEqual(d_org, d_copy)


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
        with self.assertRaises(ValueError):
            span.start = self.end

    def test_fail_on_start_greater_end(self):
        """Test if the end setter fails if start > end."""
        span = task.TimeSpan()
        span.start = self.end
        with self.assertRaises(ValueError):
            span.end = self.start

    def test_fail_2_start_greater_end(self):
        """Test if the contructor fails if start > end."""
        with self.assertRaises(ValueError):
            task.TimeSpan(self.end, self.start)

    def test_conform(self):
        """Test if it is possible to create and retrieve a TimeSpan object."""
        span_org = task.TimeSpan(start=task.Date.now(), end=task.Date.now())
        sql_str = span_org.__conform__(sqlite3.PrepareProtocol)
        span_copy = task.TimeSpan.from_sqlite(sql_str)
        self.assertEqual(span_org, span_copy)

    def test_span(self):
        """ Test if the result of time span is correct. """
        time_span = task.TimeSpan(start=self.start, end=self.end)
        self.assertEqual(time_span.time_span(), timedelta(1))


class TestState(unittest.TestCase):

    """Unittest for the StateHolder class."""

    def test_contructor(self):
        """Test if the constructor works properly."""
        state = task.StateHolder()
        self.assertEqual(state.state, task.StateHolder.pending)

    def test_contructor2(self):
        """Test if the constructor works properly with arguments."""
        for value in task.StateHolder.states.itervalues():
            state = task.StateHolder(value)
            self.assertEqual(state.state, value)

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
        """ Test if next_state fail when called on a FinalState. """
        from statemachine import FinalStateException
        state = task.StateHolder(task.StateHolder.completed)
        self.assertRaises(FinalStateException, state.next_state, "test")

    def test_get_actions(self):
        """ Test if all state return a list of actions. """
        for state in task.StateHolder.states.itervalues():
            actions = state.get_actions()
            if state.is_final():
                self.assertEqual(actions, [])
            else:
                self.assertGreater(len(actions), 0)

    def test_actions(self):
        """
        Test the action of the State holder and if we can go through them
        """
        for state in task.StateHolder.states.itervalues():
            for action in state.get_actions():
                next_state = state.next_state(action)
                self.assertIsNotNone(next_state)

    def test_fail_wrong_action(self):
        """Test if next_state fails on wrong input."""
        state = task.StateHolder(task.StateHolder.started)
        self.assertRaises(KeyError, state.next_state, "test")

    def test_conform(self):
        """Test if it is possible to create and retrieve a TimeSpan object."""
        state_org = task.StateHolder()
        sql_str = state_org.__conform__(sqlite3.PrepareProtocol)
        state_copy = task.StateHolder.from_sqlite(sql_str)
        self.assertEqual(state_org, state_copy)


class TestTask(unittest.TestCase):

    """Test for the Task class."""

    def test_constructor(self):
        """Test the constructor of the Task."""
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        self.assertEqual(tsk.title, TITLE)
        self.assertEqual(tsk.description, DESCRIPTION)

    def test_done(self):
        """ Test if we can finish a task """
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        self.assertTrue(tsk.done())
        self.assertEqual(tsk.state.state, task.StateHolder.completed)

    def test_start(self):
        """ Test if a Task can be started """
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        self.assertTrue(tsk.start())
        self.assertEqual(tsk.state.state, task.StateHolder.started)

    def test_reset(self):
        """ Test if a Task can be reset to it pending state """
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        self.assertTrue(tsk.start())
        self.assertTrue(tsk.reset())
        self.assertEqual(tsk.state.state, task.StateHolder.pending)

    def test_set_difficulty(self):
        """ Test If it is possible to set the difficulty """
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        tsk.difficulty = task.DIFFICULTY.simple
        self.assertEqual(tsk.difficulty, task.DIFFICULTY.simple)

    def test_set_false_difficulty(self):
        """ Test if a difficulty which is put of range  fails """
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        with self.assertRaises(ValueError):
            tsk.difficulty = 100


class TestAppointment(unittest.TestCase):

    """Test for the Appointments."""

    def test_constructor(self):
        """ Test the constructor of the Appointment class. """
        start = task.Date.now()
        apmt = task.Appointment(TITLE, start)

        self.assertEqual(apmt.title, TITLE)
        self.assertEqual(apmt.schedule.start, start)

    def test_start_ge_end(self):
        """ Test if the End of the Appointment can be set to a time smaller than the start time. """
        start = task.Date.now()
        apmt = task.Appointment(TITLE, start)
        end = start - timedelta(24, 0, 0)

        with self.assertRaises(ValueError):
            apmt.schedule.end = end

    def test_move(self):
        """ Move the Appointment to a new time """
        start = task.Date.now()
        new_start = start + timedelta(24, 0, 0)
        apmt = task.Appointment(TITLE, start)

        self.assertTrue(apmt.move(new_start))

        self.assertEqual(apmt.schedule.start, new_start)

    def test_move_with_end(self):
        """ Test if the End of the Appointment can be set to a time smaller than the start time. """
        start = task.Date.now()
        apmt = task.Appointment(TITLE, start)
        new_start = task.Date.now()
        new_end = start + timedelta(24, 0, 0)

        self.assertTrue(apmt.move(new_start, new_end))

        self.assertEqual(apmt.schedule.start, new_start)
        self.assertEqual(apmt.schedule.end, new_end)

    def test_move_with_start_ge_end(self):
        """ Test if the End of the Appointment can be set to a time smaller than the start time. """
        start = task.Date.now()
        end = task.Date.now() + timedelta(1, 0, 0)
        apmt = task.Appointment(TITLE, start, end=end)
        new_start = task.Date.now() + timedelta(24, 0, 0)
        new_end = new_start - timedelta(24, 0, 0)

        self.assertFalse(apmt.move(new_start, new_end))

        self.assertEqual(apmt.schedule.start, start)
        self.assertEqual(apmt.schedule.end, end)

    def test_setter(self):
        """ Test the setter methodes of Appointment """
        start = task.Date.now()
        apmt = task.Appointment(TITLE, start)

        self.assertEqual(apmt.description, None)

        new_title = "new title"
        new_description = "description one O one"

        apmt.title = new_title
        self.assertEqual(apmt.title, new_title)
        apmt.description = new_description
        self.assertEqual(apmt.description, new_description)


class TestJSONManager(unittest.TestCase):

    """Test if the task storing and loading data with the task store"""

    path = "./test/data/"

    def test_load_empty(self):
        """Test if we can load the empty file data_load_empty.doto ."""
        store = task.JSONManager(TestJSONManager.path + "data_load_empty.doto")
        self.assertEquals(store._version, 9)
        self.assertEquals(store._tasks, [])

    def test_save_load_empty(self):
        """Test if it is possible to load the saved data."""
        store = task.JSONManager(TestJSONManager.path + "data_save.doto", create=True)
        store.save()
        self.assertTrue(store.saved)
        store = task.JSONManager(TestJSONManager.path + "data_save.doto")
        self.assertEqual(store._version, 0)
        self.assertEqual(store._tasks, [])

    def test_save_load_100(self):
        """Test if we ca store 100 tasks and restore them."""
        tsk = task.Task("title", "description")
        save_store = task.JSONManager(TestJSONManager.path + "data_save_100.doto", create=True)
        for i in range(100):
            save_store.add(tsk)
        save_store.save()
        self.assertTrue(save_store.saved)
        load_store = task.JSONManager(TestJSONManager.path + "data_save_100.doto")
        for i in range(100):
            self.assertEqual(load_store._tasks[i], tsk)
        self.assertEqual(load_store._version, 0)

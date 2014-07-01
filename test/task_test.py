"""Unitests for the task module."""

import unittest
import task
from datetime import datetime, timedelta
import pytz

TITLE = "important task"
DESCRIPTION = "long description of this task \n"


class TestTimeSpan(unittest.TestCase):

    """Unittest for the TimeSpan class."""

    @classmethod
    def setUpClass(cls):
        """Set up the test data, start and end (start < end)."""
        cls.start = datetime(2011, 12, 13, 14, 15, 16)
        cls.end = datetime(2011, 12, 14, 14, 15, 16)

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
        span = task.TimeSpan(self.start)
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
        span = task.TimeSpan(self.start, self.end)
        with self.assertRaises(ValueError):
            span.start = self.end + timedelta(3)

    def test_fail_on_start_null(self):
        """Test if the start setter fails if start is None."""
        span = task.TimeSpan()
        with self.assertRaises(ValueError):
            span.end = self.end

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

    def test_span(self):
        """ Test if the result of time span is correct. """
        time_span = task.TimeSpan(start=self.start, end=self.end)
        self.assertEqual(time_span.time_span(), timedelta(1))

    def test_repr(self):
        """ Test if repr does not fail """
        time_span = task.TimeSpan(start=self.start, end=self.end)
        print repr(time_span)



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


    def test_operators(self):
        """ Test if the equal and not eqaul operators work. """
        state1 = task.StateHolder(task.StateHolder.pending)
        state2 = task.StateHolder(task.StateHolder.blocked)
        state3 = task.StateHolder(task.StateHolder.pending)

        self.assertEqual(state1, state3)
        self.assertEqual(state1, task.StateHolder.pending)
        self.assertNotEqual(state1, state2)
        self.assertNotEqual(state1, task.StateHolder.completed)

    def test_repr(self):
        """ Test if repr does not fail """
        state = task.StateHolder(task.StateHolder.started)
        print repr(state)


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

    def test_repr(self):
        """ Test if repr does not fail """
        tsk = task.Task(title=TITLE, description=DESCRIPTION)
        print repr(tsk)


class TestAppointment(unittest.TestCase):

    """Test for the Appointments."""

    def test_constructor(self):
        """ Test the constructor of the Appointment class. """
        start = task.now_with_tz()
        apmt = task.Appointment(TITLE, start)

        self.assertEqual(apmt.title, TITLE)
        self.assertEqual(apmt.schedule.start, start)

    def test_start_ge_end(self):
        """ Test if the End of the Appointment can be set to a time smaller than the start time. """
        start = task.now_with_tz()
        apmt = task.Appointment(TITLE, start)
        end = start - timedelta(24, 0, 0)

        with self.assertRaises(ValueError):
            apmt.schedule.end = end

    def test_move(self):
        """ Move the Appointment to a new time """
        start = task.now_with_tz()
        new_start = start + timedelta(24, 0, 0)
        apmt = task.Appointment(TITLE, start)

        self.assertTrue(apmt.move(new_start))

        self.assertEqual(apmt.schedule.start, new_start)

    def test_move_with_end(self):
        """ Test if the End of the Appointment can be set to a time smaller than the start time. """
        start = task.now_with_tz()
        apmt = task.Appointment(TITLE, start)
        new_start = task.now_with_tz()
        new_end = start + timedelta(24, 0, 0)

        self.assertTrue(apmt.move(new_start, new_end))

        self.assertEqual(apmt.schedule.start, new_start)
        self.assertEqual(apmt.schedule.end, new_end)

    def test_move_with_start_ge_end(self):
        """ Test if the End of the Appointment can be set to a time smaller than the start time. """
        start = task.now_with_tz()
        end = task.now_with_tz() + timedelta(1, 0, 0)
        apmt = task.Appointment(TITLE, start, end=end)
        new_start = task.now_with_tz() + timedelta(24, 0, 0)
        new_end = new_start - timedelta(24, 0, 0)

        self.assertFalse(apmt.move(new_start, new_end))

        self.assertEqual(apmt.schedule.start, start)
        self.assertEqual(apmt.schedule.end, end)

    def test_setter(self):
        """ Test the setter methodes of Appointment """
        start = task.now_with_tz()
        apmt = task.Appointment(TITLE, start)

        self.assertEqual(apmt.description, None)

        new_title = "new title"
        new_description = "description one O one"

        apmt.title = new_title
        self.assertEqual(apmt.title, new_title)
        apmt.description = new_description
        self.assertEqual(apmt.description, new_description)

    def test_repr(self):
        """ Test if repr does not fail """
        apmt = task.Appointment(TITLE, task.now_with_tz())
        print repr(apmt)

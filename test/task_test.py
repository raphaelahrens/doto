import unittest

import task


title = "important task"
description = "long description of this task \n"


class TestDate(unittest.TestCase):
    def test_constructor(self):
        from datetime import datetime
        d1 = datetime(2011, 12, 13, 14, 15, 16)
        d2 = task.Date(2011, 12, 13, 14, 15, 16)

        self.assertEqual(d1, d2)


class TestTimeSpan(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.start = task.Date(2011, 12, 13, 14, 15, 16)
        cls.end = task.Date(2011, 12, 14, 14, 15, 16)

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


class TestJSONCoder(unittest.TestCase):
    """
    Test for the JSON de- and encoder
    """
    def setUp(self):
        self.en = task.TaskEncoder()

    def test_encode(self):
        """
        Test the constructor of the encoder
        """
        t = task.Task(title=title, description=description)
        self.en.encode(t)

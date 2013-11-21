import unittest
import task
import serializer


class TestEncoder(unittest.TestCase):
    """
    Test for the JSON de- and encoder
    """
    def test_encode(self):
        """
        Test the constructor of the encoder
        """
        en = serializer.TaskEncoder()
        t = task.Task(title="test task", description="long description")
        en.encode(t)


class TestDecoder(unittest.TestCase):
    def test_constructor(self):
        serializer.TaskDecoder()


class TestDeAndEnCoder(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.en = serializer.TaskEncoder()
        cls.de = serializer.TaskDecoder()

    def test_Date(self):
        date_org = task.Date.now()
        date_code = self.en.encode(date_org)
        date_copy = self.de.decode(date_code)
        self.assertEqual(date_org, date_copy)

    def test_TimeSpan(self):
        span_org = task.TimeSpan()
        span_code = self.en.encode(span_org)
        span_copy = self.de.decode(span_code)
        self.assertEqual(span_org, span_copy)

    def test_TimeSpan2(self):
        start = task.Date.local(2010, 10, 1)
        end = task.Date.local(2010, 12, 1)
        span_org = task.TimeSpan(start, end)
        span_code = self.en.encode(span_org)
        span_copy = self.de.decode(span_code)
        self.assertEqual(span_org, span_copy)

    def test_Task(self):
        task_org = task.Task("one task", "long description")
        json_code = self.en.encode(task_org)
        task_copy = self.de.decode(json_code)
        self.assertEqual(task_org, task_copy)

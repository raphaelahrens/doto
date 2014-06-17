"""Unitests for the serializer module."""

import unittest
import task
import serializer


class TestEncoder(unittest.TestCase):

    """Test for the JSON de- and encoder."""

    def test_encode(self):
        """Test the constructor of the encoder."""
        en = serializer.TaskEncoder()
        t = task.Task(title="test task", description="long description")
        s = en.encode(t)
        self.assertTrue(type(s) == str)


class TestDecoder(unittest.TestCase):

    """Test fort the Taskdecoder."""

    def test_constructor(self):
        """Test the constructor of TaskDecoder."""
        de = serializer.TaskDecoder()
        self.assertTrue(type(de) == serializer.TaskDecoder)


class TestDeAndEnCoder(unittest.TestCase):

    """Test for de- and encoding all subclasses of JSONSerialize."""

    @classmethod
    def setUpClass(cls):
        """Set up the de- and encoder for the following tests."""
        cls.en = serializer.TaskEncoder()
        cls.de = serializer.TaskDecoder()

    def test_Date(self):
        """Test if Date can be serialized."""
        date_org = task.Date.now()
        date_code = self.en.encode(date_org)
        date_copy = self.de.decode(date_code)
        self.assertEqual(date_org, date_copy)

    def test_State(self):
        """Test if State can be serialized."""
        state_org = task.StateHolder()
        code = self.en.encode(state_org)
        copy = self.de.decode(code)
        self.assertEqual(state_org, copy)

    def test_TimeSpan(self):
        """Test if an empty TimeSpan can be serialized."""
        span_org = task.TimeSpan()
        span_code = self.en.encode(span_org)
        span_copy = self.de.decode(span_code)
        self.assertEqual(span_org, span_copy)

    def test_TimeSpan2(self):
        """Test if TimeSpan with end and start can be serialized."""
        start = task.Date.local(2010, 10, 1)
        end = task.Date.local(2010, 12, 1)
        span_org = task.TimeSpan(start, end)
        span_code = self.en.encode(span_org)
        span_copy = self.de.decode(span_code)
        self.assertEqual(span_org, span_copy)

    def test_Task(self):
        """Test if Task can be serialized."""
        task_org = task.Task("one task", "long description")
        json_code = self.en.encode(task_org)
        task_copy = self.de.decode(json_code)
        self.assertEqual(task_org, task_copy)

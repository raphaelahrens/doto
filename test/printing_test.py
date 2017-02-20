
"""Unitests for the cli.printing module"""

import unittest
import datetime
import doto.cli.printing
import doto.dbmodel


class TestStrFromTimeSpan(unittest.TestCase):

    """Unittest for the Printing Module."""

    now = doto.dbmodel.now_with_tz()

    def test_one_sec(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 1, 0)
        span = doto.dbmodel.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "1 second")

    def test_two_secs(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 2, 0)
        span = doto.dbmodel.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "2 seconds")

    def test_one_min(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 60, 0)
        span = doto.dbmodel.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "1 minute")

    def test_two_min(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 120, 0)
        span = doto.dbmodel.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "2 minutes")

    def test_one_day(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(1, 0, 0)
        span = doto.dbmodel.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "1 day")

    def test_two_days(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(2, 120, 0)
        span = doto.dbmodel.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "2 days")

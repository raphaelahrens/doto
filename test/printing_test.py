
"""Unitests for the cli.printing module"""

import unittest
import datetime
import doto.cli.printing
import doto.model


class TestStrFromTimeSpan(unittest.TestCase):

    """Unittest for the Printing Module."""

    now = doto.model.now_with_tz()

    def test_one_sec(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 1, 0)
        span = doto.model.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "1 second")

    def test_two_secs(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 2, 0)
        span = doto.model.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "2 seconds")

    def test_one_min(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 60, 0)
        span = doto.model.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "1 minute")

    def test_two_min(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(0, 120, 0)
        span = doto.model.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "2 minutes")

    def test_one_day(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(1, 0, 0)
        span = doto.model.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "1 day")

    def test_two_days(self):
        now_plus_x = TestStrFromTimeSpan.now + datetime.timedelta(2, 120, 0)
        span = doto.model.TimeSpan(TestStrFromTimeSpan.now, now_plus_x)
        result = doto.cli.printing.str_from_time_delta(span.time_delta())
        self.assertEqual(result, "2 days")


class TestUnicodeFromatter(unittest.TestCase):
    def test_empty(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        self.assertEqual('', formatter.format(''))

    def test_int(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        self.assertEqual('11', formatter.format('{}', 11))

    def test_float(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        self.assertEqual('11.0', formatter.format('{}', 11.0))

    def test_simple_inster(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        format_spec = '{}'
        test_str = 'Testa̲'
        self.assertEqual(test_str, formatter.format(format_spec, test_str))
        test_str = 'test'
        self.assertEqual(format_spec.format(test_str), formatter.format(format_spec, test_str))

    def test_left_pad(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        format_spec = '{:<10}'
        test_str = 'test'
        self.assertEqual(format_spec.format(test_str), formatter.format(format_spec, test_str))
        utest_str = 'Testa̲'
        self.assertEqual(format_spec.format(utest_str) + ' ', formatter.format(format_spec, utest_str))

    def test_right_pad(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        format_spec = '{:>10}'
        test_str = "test"
        self.assertEqual(format_spec.format(test_str), formatter.format(format_spec, test_str))
        utest_str = 'Testa̲'
        self.assertEqual(' ' + format_spec.format(utest_str), formatter.format(format_spec, utest_str))

    def test_center_pad(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        format_spec = '{:^10}'
        test_str = "test"
        self.assertEqual(format_spec.format(test_str), formatter.format(format_spec, test_str))
        utest_str = 'Testa̲'
        self.assertEqual(format_spec.format(utest_str) + ' ', formatter.format(format_spec, utest_str))

    def test_center_pad_fill(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        format_spec = '{:^10}'
        test_str = "test"
        self.assertEqual(format_spec.format(test_str), formatter.format(format_spec, test_str))
        utest_str = 'Testa̲'
        self.assertEqual(format_spec.format(utest_str) + ' ', formatter.format(format_spec, utest_str))

    def test_unicode_pad(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        utest_str = 'Tet̲a̲r̲st'
        format_specs = (('{:<10}', utest_str + '   '),
                        ('{:>10}', '   ' + utest_str),
                        ('{:^10}', ' ' + utest_str + '  ')
                        )
        for spec, t_str in format_specs:
            self.assertEqual(t_str, formatter.format(spec, utest_str))

    def test_zero_pad(self):
        formatter = doto.cli.printing.UnicodeFormatter()
        utest_str = 'Tet̲a̲r̲st'
        format_specs = (('{:<010}', utest_str + '000'),
                        ('{:>010}', '000' + utest_str),
                        ('{:^010}', '0' + utest_str + '00')
                        )
        for spec, t_str in format_specs:
            self.assertEqual(t_str, formatter.format(spec, utest_str))

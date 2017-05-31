# -*- coding: utf-8 -*-
"""
A Collection of functions to display tasks and other data.
"""

import datetime
import itertools
import math
import string

import doto.model.task
import pytz
import wcwidth


__state_symbols = {doto.model.task.StateHolder.completed.key: "✓",
                   doto.model.task.StateHolder.blocked.key: "✗",
                   doto.model.task.StateHolder.interrupted.key: "↯",
                   doto.model.task.StateHolder.pending.key: " ",
                   doto.model.task.StateHolder.started.key: "▶"
                   }

__state_strings = {doto.model.task.StateHolder.completed.key: "completed",
                   doto.model.task.StateHolder.blocked.key: "blocked",
                   doto.model.task.StateHolder.interrupted.key: "interrupted",
                   doto.model.task.StateHolder.pending.key: "pending",
                   doto.model.task.StateHolder.started.key: "started"
                   }

__difficulty_symbols = {doto.model.task.DIFFICULTY.unknown: " ",
                        doto.model.task.DIFFICULTY.simple: "Ⅰ",
                        doto.model.task.DIFFICULTY.easy: "Ⅱ",
                        doto.model.task.DIFFICULTY.medium: "Ⅲ",
                        doto.model.task.DIFFICULTY.hard: "Ⅳ",
                        }


ZERO_DELTA = datetime.timedelta(0)
STR_THRESHOLD = datetime.timedelta(days=7)
ONE_MINUTE = datetime.timedelta(seconds=60)


def state_to_symbol(state):
    return __state_symbols[state.key]


def state_to_str(state):
    return __state_strings[state.key]


def diff_to_str(difficulty):
    return __difficulty_symbols[difficulty]


def one_or_more(amount, single_str, multiple_str):
    """
    Return a string which uses either the single or the multiple form.

    @param amount the amount to be displayed
    @param single_str the string for a single element
    @param multiple_str the string for multiple elements

    @return the string representation

    """
    if amount == 1:
        ret_str = single_str
    else:
        ret_str = multiple_str
    return ret_str.format(amount)


def str_from_time_delta(t_delta):
    """
    Create a pretty string representation of a Time span.

    The function returns a string that is a natural representation
    of the time span. For example "1 day", "2 days", "3 hours", ...

    @param t_delta a datetime.timedelta object

    @return the string

    """
    def check_zero_time(fmt_time):
        _, time = fmt_time
        return time == 0

    if t_delta < ONE_MINUTE:
        return 'soon'

    days = t_delta.days
    hours = t_delta.seconds // 3600
    minutes = t_delta.seconds % 3600 // 60

    format_strs = ['{}d', '{}h', '{}m']
    times = [days, hours, minutes]

    fmt_times = itertools.dropwhile(check_zero_time, zip(format_strs, times))

    return ' '.join(fmt.format(time) for fmt, time in fmt_times)


def max_date_len(date_to_str):
    def date_len(date):
        return len(date_to_str(date))

    def find_max_index(lst):
        return max(range(len(lst)), key=lst.__getitem__)

    # run through all month and add 1 to the return index which is between 0
    # and 11. But we need a number between 1 and 12 since it is a month :(
    max_month = 1 + find_max_index([date_len(datetime.datetime(2012, month, 12, 12, 12, tzinfo=pytz.utc)) for month in range(1, 13)])

    # run throw all days of the week from day 10 to 16 since
    # this covers all weekdays and double digit days
    return max([date_len(datetime.datetime(2012, max_month, day, 12, 12, tzinfo=pytz.utc)) for day in range(10, 17)])


class DatePrinter(object):
    def __init__(self, config):
        self.__config = config

        self.__max_date_len = max_date_len(self.short_date_string)

    def due_to_str(self, due_date, default=""):
        if due_date is None:
            return default
        t_delta = due_date - doto.model.now_with_tz()
        if t_delta < ZERO_DELTA:
            # the time span is negative so the time is over due
            return "over due"
        if t_delta <= STR_THRESHOLD:
            # if the time span is smaller than one week
            # return the time span string
            return str_from_time_delta(t_delta)
        # return the string if it is over one week
        return self.date_to_str(due_date)

    def to_local(self, date_obj):
        local_tz = pytz.timezone(self.__config.date.local_tz)
        return date_obj.astimezone(local_tz)

    def short_date_string(self, date):
        local_date = self.to_local(date)
        return '{:{fmt}}'.format(local_date, fmt=self.__config.date.short_out_str)

    def full_date_string(self, date):
        local_date = self.to_local(date)
        return '{:{fmt}}'.format(local_date, fmt=self.__config.date.full_out_str)

    @property
    def max_due_len(self):
        return self.max_date_len

    def date_to_str(self, date, default=""):
        if date is None:
            return default
        return self.short_date_string(date)

    @property
    def max_date_len(self):
        return self.__max_date_len


class UnicodeFormatter(string.Formatter):
    def format_field(self, value, format_spec):
        if not isinstance(value, str):
            # If `value` is not a string use format built-in
            return format(value, format_spec)
        if format_spec == '':
            # If `format_spec` is empty we just return the `value` string
            return value

        print_length = wcwidth.wcswidth(value)
        if len(value) == print_length:
            return format(value, format_spec)

        fill, align, width, format_spec = UnicodeFormatter.parse_align(format_spec)
        if width == 0:
            return value
        formatted_value = format(value, format_spec)
        pad_len = width - print_length
        if pad_len <= 0:
            return formatted_value
        left_pad = ''
        right_pad = ''
        if align in '<=':
            right_pad = fill * pad_len
        elif align == '>':
            left_pad = fill * pad_len
        elif align == '^':
            left_pad = fill * math.floor(pad_len/2)
            right_pad = fill * math.ceil(pad_len/2)
        return ''.join((left_pad, formatted_value, right_pad))

    @staticmethod
    def parse_align(format_spec):
        format_chars = '=<>^'
        align = '<'
        fill = None
        if format_spec[1] in format_chars:
            align = format_spec[1]
            fill = format_spec[0]
            format_spec = format_spec[2:]
        elif format_spec[0] in format_chars:
            align = format_spec[0]
            format_spec = format_spec[1:]

        if align == '=':
            raise ValueError("'=' alignment not allowed in string format specifier")
        if format_spec[0] in '+- ':
            raise ValueError('Sign not allowed in string format specifier')
        if format_spec[0] == '#':
            raise ValueError('Alternate form (#) not allowed in string format specifier')
        if format_spec[0] == '0':
            if fill is None:
                fill = '0'
            format_spec = format_spec[1:]
        if fill is None:
            fill = ' '
        width_str = ''.join(itertools.takewhile(str.isdigit, format_spec))
        width_len = len(width_str)
        format_spec = format_spec[width_len:]
        if width_len > 0:
            width = int(width_str)
        else:
            width = 0
        return fill, align, width, format_spec

# -*- coding: utf-8 -*-
"""
A Collection of functions to display tasks and other data.
"""

import datetime
import dbmodel
import pytz


__state_symbols = {dbmodel.StateHolder.completed.key: u"✓",
                   dbmodel.StateHolder.blocked.key: u"✗",
                   dbmodel.StateHolder.interrupted.key: u"↯",
                   dbmodel.StateHolder.pending.key: u" ",
                   dbmodel.StateHolder.started.key: u"▶"
                   }

__state_strings = {dbmodel.StateHolder.completed.key: u"completed",
                   dbmodel.StateHolder.blocked.key: u"blocked",
                   dbmodel.StateHolder.interrupted.key: u"interrupted",
                   dbmodel.StateHolder.pending.key: u"pending",
                   dbmodel.StateHolder.started.key: u"started"
                   }

__difficulty_symbols = {dbmodel.DIFFICULTY.unknown: u" ",
                        dbmodel.DIFFICULTY.simple: u"Ⅰ",
                        dbmodel.DIFFICULTY.easy: u"Ⅱ",
                        dbmodel.DIFFICULTY.medium: u"Ⅲ",
                        dbmodel.DIFFICULTY.hard: u"Ⅳ",
                        }


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
    return ret_str % amount


def str_from_time_span(t_span):
    """
    Create a pretty string representation of a Time span.

    The function returns a string that is a natural representation
    of the time span. For example "1 day", "2 days", "3 hours", ...


    @return the string

    """
    if t_span.days < 0:
        raise
    if t_span.days > 0:
        return one_or_more(t_span.days, "%d day", "%d days")
    if t_span.seconds > 3600:
        return one_or_more(t_span.seconds // 3600, "%d hour", "%d hours")
    if t_span.seconds > 60:
        return one_or_more(t_span.seconds // 60, "%d minute", "%d minutes")
    return one_or_more(t_span.seconds, "%d second", "%d seconds")


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

    def due_to_str(self, due_date, default=u""):
        if due_date is None:
            return default
        t_span = due_date - dbmodel.now_with_tz()
        if t_span.days < 0:
            # the time span is negativ so the time is over due
            return u"over due"
        if t_span.days < 7:
            # if the time span is smaller than one week
            # return the time span string
            return u"in " + str_from_time_span(t_span)
        # return the string if it is over one week
        return u"to " + self.date_to_str(due_date)

    def to_local(self, date_obj):
        local_tz = pytz.timezone(self.__config.date.local_tz)
        return date_obj.astimezone(local_tz)

    def short_date_string(self, date):
        return self.to_local(date).strftime(self.__config.date.short_out_str)

    def full_date_string(self, date):
        return self.to_local(date).strftime(self.__config.date.full_out_str)

    @property
    def max_due_len(self):
        return len(u"to ") + self.max_date_len

    def date_to_str(self, date, default=u""):
        if date is None:
            return default
        return self.short_date_string(date)

    @property
    def max_date_len(self):
        return self.__max_date_len

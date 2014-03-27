# -*- coding: utf-8 -*-
"""
Small utilities for the cli commands.
"""
__all__ = ["uprint", "print_table", ]

import locale
LOCAL_ENCODING = locale.getdefaultlocale()[1]


def to_unicode(string):
    return string.decode(LOCAL_ENCODING)


def uprint(string):
    """
    Print the given string to standard out.

    The string is encoded to UTF-8.

    @param string the string that will be printed and encoded to UTF-8

    """
    print unicode(string).encode(LOCAL_ENCODING)


def uprint_list(strings):
    """
    Print a collection of strings to standard out.

    Every string in strings will be encoded to UTF-8.

    @param strings a collection of strings.

    """
    for string in strings:
        uprint(string)


def to_str(obj):
    """
    Turn the given object into a string.

    If the obj is None the result will be an empty string.

    @return a string representation of obj. If obj is None the string is empty.

    """
    if obj is None:
        return u""
    return unicode(obj)


LINES = {"v": unichr(0x2502),
         "+": unichr(0x253c),
         "h": unichr(0x2500)
         }

ID_FORMAT = "%d [%08x]"


def print_table(columns, data):
    """
    Print a table to standard out with the given columns and the given data.

    A column item needs to have a name of type string and a width of type int.
    The function first prints the column and then for each item in data it
    prints a row in the table. Therefor the length of each data tuple needs to
    be equal to the number of columns.

    @param columns a list of tuples with (str, int) values
    @param data a list of tuples
           where len(data[x]) == len(columns) with 0 <= x < len(data)

    """
    table = Table(columns)
    table.print_multiple_rows(data)


class Table(object):
    def __init__(self, columns):
        self._column_count = len(columns)
        header = []
        divider = []
        row_format = []
        for name, width in columns:
            if width < len(name):
                width = len(name)
            header.append(("{:%s%d}" % ("^", width)).format(name))
            divider.append(LINES["h"] * width)
            row_format.append("{:%s%d}" % ("<", width))
        uprint(LINES["v"].join(header))
        uprint(LINES["+"].join(divider))
        self._row_format = LINES["v"].join(row_format)

    def print_row(self, data):
        assert len(data) == self._column_count
        uprint(self._row_format.format(*data))

    def print_multiple_rows(self, data_list):
        for data in data_list:
            self.print_row(data)


def get_cached_task(store, task_id):
    cache = store.get_cache()
    if not cache:
        tasks = store.get_tasks()
        if tasks:
            uprint("I don't know which task you want!\nYou should first run:\n\tdoto ls")
            return None, 3
        uprint("There are no tasks.\nMaybe you would first like to add a new task with: \n\t doto add \"title\" \"description\" ")
        return None, 2

    if task_id not in cache:
        uprint("There is no task with the id %d" % task_id)
        return None, 1
    cached_task = cache[task_id]
    return cached_task, 0

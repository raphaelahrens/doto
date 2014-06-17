# -*- coding: utf-8 -*-
"""
Small utilities for the cli commands.
"""
__all__ = ["uprint"]

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

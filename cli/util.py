# -*- coding: utf-8 -*-
"""
Small utilities for the cli commands.
"""
import locale

LOCAL_ENCODING = locale.getdefaultlocale()[1]


def print_list(strings):
    """
    Print a collection of strings to standard out.

    Every string in strings will be encoded to UTF-8.

    @param strings a collection of strings.

    """
    for string in strings:
        print(string)


def to_str(obj):
    """
    Turn the given object into a string.

    If the obj is None the result will be an empty string.

    @return a string representation of obj. If obj is None the string is empty.

    """
    if obj is None:
        return ""
    return str(obj)


LINES = {"v": chr(0x2502),
         "+": chr(0x253c),
         "h": chr(0x2500)}

ID_FORMAT = "%d [%08x]"


def get_cached_task(store, cache_id):
    """
    Get the cached task with the cache_id from the given store.

    @param store the store that stores all tasks
    @param cache_id the id of the cached task
    """
    cache_item, cache_error = store.get_cache_item(cache_id)
    if not cache_item:
        if not cache_error:
            print("There is no task with the id %d" % cache_id)
            return None, 1

        if store.get_task_count() > 0:
            print("I don't know which task you want!\nYou should first run:\n\tdoto ls")
            return None, 3
        print("There are no tasks.\nMaybe you would first like to add a new task with: \n\t doto add \"title\" \"description\" ")
        return None, 2

    return cache_item, 0

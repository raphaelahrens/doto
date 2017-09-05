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


ID_FORMAT = "%d [%08x]"

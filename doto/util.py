# -*- coding: utf-8 -*-
"""
The util module holds miscellaneous utility functions
"""


def enum(*sequential, **named):
    """
    A simple enum implementation.

    @return a enum object

    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    keys = list(enums.keys())
    ident = enums.copy()
    enums['keys'] = keys
    enums['ident'] = ident.get
    return type('Enum', (), enums)


def partition(pred, iterable):
    """
    Partion a list in two lists
    where the first list hold all items
    for which the function pred returned True
    and the second list holds all reset.

    @param pred a function that returns True or False and has one parameter
    @param iterable a list of items which can be called with pred

    @returns two list one with all items for which pred returned True
                and a second list with all items for which pred returned False
    """
    trues = []
    falses = []
    for item in iterable:
        if pred(item):
            trues.append(item)
        else:
            falses.append(item)
    return trues, falses

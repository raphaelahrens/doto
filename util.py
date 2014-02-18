# -*- coding: utf-8 -*-
def enum(*sequential, **named):
    """
    A simple enum implementation.

    @return a enum object

    """
    enums = dict(zip(sequential, range(len(sequential))), **named)
    keys = list(value for value in enums.iterkeys())
    ident = enums.copy()
    enums['keys'] = keys
    enums['ident'] = ident.get
    return type('Enum', (), enums)

# -*- coding: utf-8 -*-
__all__ = ["uprint", "print_table", ]


def uprint(string):
    print unicode(string).encode("utf-8")


def to_str(obj):
    if obj is None:
        return ""
    return str(obj)


lines = {"v": unichr(0x2502),
         "+": unichr(0x253c),
         "h": unichr(0x2500)
         }


def print_table(columns, data):
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
            divider.append(lines["h"] * width)
            row_format.append("{:%s%d}" % ("<", width))
        uprint(lines["v"].join(header))
        uprint(lines["+"].join(divider))
        self._row_format = lines["v"].join(row_format)

    def print_row(self, data):
        assert(len(data) == self._column_count)
        uprint(self._row_format.format(*data))

    def print_multiple_rows(self, data_list):
        for data in data_list:
            self.print_row(data)

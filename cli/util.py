__all__ = ["uprint", "print_table"]

import itertools


def uprint(string):
    print unicode(string).encode("utf-8")


def to_str(obj):
    if obj is None:
        return ""
    return str(obj)


def align(string, length, orientation="left"):
    extra_space = length - len(string)
    if extra_space < 0:
        extra_space = 0
    if orientation == "middle":
        side_space = " " * ((extra_space) / 2)
        return side_space + string + side_space + " " * (extra_space % 2)
    if orientation == "left":
        return string + extra_space * " "
    if orientation == "right":
        return " " * extra_space + string


lines = {"v": unichr(0x2502),
         "+": unichr(0x253c),
         "h": unichr(0x2500)
         }


def print_column_names(column_names):
    if len(column_names) < 1:
        raise Exception("too few column_names")
    lengths = []
    header_strings = []
    dividers = []
    for header, length in column_names:
        if length < len(header):
            length = len(header)
        lengths.append(length)
        header_strings.append(align(header, length, "middle"))
        dividers.append(lines["h"] * length)
    uprint(lines["v"].join(header_strings))
    uprint(lines["+"].join(dividers))
    return lengths


def print_line(values, lengths):
    if len(values) != len(lengths):
        raise Exception("too few values")
    strings = [align(to_str(value)[:length], length, "left") for value, length in itertools.izip(values, lengths)]
    return lines["v"].join(strings)


def print_table(column_names, data):
    lengths = print_column_names(column_names)
    for values in data:
        uprint(print_line(values, lengths))

# -*- coding: utf-8 -*-
"""
The command ls list all open tasks.

An example of its use is
    $ doto ls

"""
import cli.util
import cli.printing
import textwrap
import itertools


COMMAND = "ls"
CONF_DEF = {}


class Column(object):
    def __init__(self, name, width, align, display_fn=unicode):
        self._name = name
        len_name = len(name)
        self._width = width if width >= len_name else len_name
        self._display_fn = display_fn
        self.__align = "<"
        if align == "center":
            self.__align = "^"
        elif align == "right":
            self.__align = ">"

    @property
    def align(self):
        return self.__align

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    def pack(self, data):
        return [self._display_fn(data)]


class WrapColumn(Column):
    def __init__(self, name, width, align, display_fn=unicode):
        Column.__init__(self, name, width, align, display_fn)
        self._wrapper = textwrap.TextWrapper(width=self._width,
                                             expand_tabs=False,
                                             subsequent_indent=u"  "
                                             )

    def pack(self, data):
        return self._wrapper.wrap(self._display_fn(data))


class CutColumn(Column):
    def __init__(self, name, width, align, display_fn=unicode):
        Column.__init__(self, name, width, align,  display_fn)

    def pack(self, data):
        return [self._display_fn(data)[:self._width]]


class LineIterator(object):
    def __init__(self, columns, data):
        self.__columns = columns
        self.__data = data
        self.__data_iter = iter(data)
        self.__line_iter = iter([])

    def __iter__(self):
        self.__data_iter = iter(self.__data)
        return self

    def next(self):
        try:
            return self.__line_iter.next()
        except StopIteration:
            # ignore since we might have more in the data_iter
            pass

        items = [column.pack(date) for column, date in zip(self.__columns, self.__data_iter.next())]
        self.__line_iter = itertools.izip_longest(*items, fillvalue="")
        return self.next()


class Table(object):
    def __init__(self, columns):
        self._columns = columns
        header = []
        divider = []
        row_format = []
        for each in columns:
            header.append(("{:%s%d}" % ("^", each.width)).format(each.name))
            divider.append(u"─" * each.width)
            row_format.append("{:%s%d}" % (each.align, each.width))
        cli.util.uprint(u" ".join(header))
        cli.util.uprint(u"┼".join(divider))
        self._row_format = u"│".join(row_format)

    def print_rows(self, data_list):
        for line_data in LineIterator(self._columns, data_list):
            cli.util.uprint(self._row_format.format(*line_data))


def init_parser(subparsers):
    """Initialize the subparser of ls."""
    parser = subparsers.add_parser(COMMAND, help="list tasks.")
    parser.add_argument("--all", action="store_true", help="list all tasks.")


class View(object):

    def __init__(self, config, columns):
        self._table = Table(columns)

    def print_view(self, tasks):
        self._table.print_rows(self._get_data(tasks))

    def _get_data(self, tasks):
        raise NotImplemented()


class Overview(View):
    def __init__(self, config, width):
        columns = [CutColumn("ID", 4, "right"),
                   Column("S", 1, "center", cli.printing.state_to_symbol),
                   Column("D", 1, "center", cli.printing.diff_to_str),
                   Column("Due", 13, "center", cli.printing.get_due_to_str(config)),
                   WrapColumn("Title", max(0, width - 23), "left")
                   ]
        View.__init__(self, config, columns)

    def _get_data(self, tasks):
        return ((cache_id,
                 tsk.state,
                 tsk.difficulty,
                 tsk.schedule.due,
                 tsk.title
                 )
                for cache_id, tsk in zip(range(len(tasks)), tasks))


def main(store, args, config, term):
    """
    List all open tasks.

    If args.all is given show all the tasks.

    """
    if args.all:
        tasks = store.get_tasks(True, limit=-1)
    else:
        tasks = store.get_open_tasks(True)

    view = Overview(config, term.width if term.width else 80)
    view.print_view(tasks)
    return 0

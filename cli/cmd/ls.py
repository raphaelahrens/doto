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
import util


COMMAND = "ls"
CONF_DEF = {}


class Column(object):
    def __init__(self, name, width, align, display_fn=unicode, expand=None):
        self._name = name
        len_name = len(self._name)
        self._width = width if width >= len_name else len_name
        self._display_fn = display_fn
        self.__align = "<"
        if align == "center":
            self.__align = "^"
        elif align == "right":
            self.__align = ">"

        self.__expand = expand

    @property
    def align(self):
        return self.__align

    @property
    def name(self):
        return self._name

    @property
    def width(self):
        return self._width

    @property
    def expand(self):
        return self.__expand

    def pack(self, data):
        return [self._display_fn(data)]

    def set_width(self, width):
        self._width = width if width > self._width else self._width


class WrapColumn(Column):
    def __init__(self, name, width, align, display_fn=unicode, expand=None):
        Column.__init__(self, name, width, align, display_fn, expand=expand)
        self._wrapper = textwrap.TextWrapper(width=self._width,
                                             expand_tabs=False,
                                             subsequent_indent=u"  "
                                             )

    def pack(self, data):
        return self._wrapper.wrap(self._display_fn(data))

    def set_width(self, width):
        Column.set_width(self, width)
        self._wrapper.width = self._width


class CutColumn(Column):
    def __init__(self, name, width, align, display_fn=unicode, expand=None):
        Column.__init__(self, name, width, align,  display_fn, expand=expand)

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


class View(object):

    def __init__(self, config, width, columns):
        fixed_columns, expanding_columns = util.partition(lambda x: x.expand is None, columns)
        fix_size = sum((column.width for column in fixed_columns))
        expand_sum = sum(column.expand for column in expanding_columns)
        rest_size = max(0, width - fix_size - len(columns))
        for column in expanding_columns:
            column.set_width((rest_size * column.expand) // expand_sum)

        self._table = Table(columns)

    def print_view(self, tasks):
        self._table.print_rows(self._get_data(tasks))

    def _get_data(self, tasks):
        raise NotImplemented()


class Overview(View):
    def __init__(self, config, width):
        date_printer = cli.printing.DatePrinter(config)
        columns = [CutColumn("ID", 4, "right"),
                   Column("S", 1, "center", cli.printing.state_to_symbol),
                   Column("D", 1, "center", cli.printing.diff_to_str),
                   Column("Due", date_printer.max_due_len, "center", date_printer.due_to_str),
                   WrapColumn("Title", 10, "left", expand=1)
                   ]
        View.__init__(self, config, width, columns)

    def _get_data(self, tasks):
        return ((cache_id,
                 tsk.state,
                 tsk.difficulty,
                 tsk.due,
                 tsk.title
                 )
                for cache_id, tsk in zip(range(len(tasks)), tasks))


class ApmtOverview(View):
    def __init__(self, config, width):
        date_printer = cli.printing.DatePrinter(config)
        columns = [CutColumn("ID", 4, "right"),
                   Column("Starts", date_printer.max_due_len + 4, "center", date_printer.due_to_str),
                   WrapColumn("Title", 10, "left", expand=1)
                   ]
        View.__init__(self, config, width, columns)

    def _get_data(self, apmts):
        return ((cache_id,
                 tsk.schedule.due,
                 tsk.title
                 )
                for cache_id, tsk in zip(range(len(apmts)), apmts))


class EventOverview(object):
    def __init__(self, config, width):
        self.__head_line_format = "{:^%d}" % width
        self.__task_view = TaskOverview(config, width)
        self.__apmt_view = ApmtOverview(config, width)

    def _print_headline(self, head_line):
        cli.util.uprint(self.__head_line_format.format(head_line))

    def print_view(self, tasks):
        self._print_headline("Appointments:")
        self.__apmt_view.print_view(tasks[:3])
        self._print_headline("Tasks:")
        self.__task_view.print_view(tasks)

__default_view = "overview"


__views = {__default_view: EventOverview,
           "tasks": TaskOverview,
           "apmts": None,
           }


def init_parser(subparsers):
    """Initialize the subparser of ls."""

    parser = subparsers.add_parser(COMMAND, help="list tasks.")
    parser.add_argument("view", type=cli.parser.to_unicode, default=__default_view, nargs="?",
                        choices=__views.keys())
    parser.add_argument("--all", action="store_true", help="list all tasks.")
    parser.add_argument("--limit", type=int, help="show a mximum of N tasks.", default=20)


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

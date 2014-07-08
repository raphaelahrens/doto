# -*- coding: utf-8 -*-
"""
The command ls list all open tasks.

An example of its use is
    $ doto ls

"""
import abc
import cli.util
import cli.printing
import textwrap
import itertools
import util
import task
import datetime


COMMAND = "ls"
CONF_DEF = {}


class Column(object):
    """
    Column is  defines how a column in a Table object looks like.

    A Column needs
       * name         a name which is used as a header

       * width        that defines the width of this column
                      also compared to the other columns

       * align        an alignment for the printed data

       * display_fn   a function for converting data into a

       * expand      expand defines how much space a column can occupy in
                     addition to the normal width. This depends on the other
                     columns in the table.

    """
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
        """ Get the alignment. """
        return self.__align

    @property
    def name(self):
        """ Get the name. """
        return self._name

    @property
    def width(self):
        """ Get the width of the column. """
        return self._width

    @property
    def expand(self):
        """ Get if this Column can expand and how much of the unoccupied space it wants. """
        return self.__expand

    def pack(self, data):
        """
        Take the data and pack into the column format.

        @param data the data that will be packed into the format

        @return an iteratable with the packed data
        """
        return (self._display_fn(data),)

    def set_width(self, width):
        """
        Set the widths of this Column.

        This method can becalled if the width of the column can be enlarged.

        If the parameter width is smaller then the member variable width, then this method has no effect

        @param width the new width
        """
        self._width = width if width > self._width else self._width


class WrapColumn(Column):
    """
    WrapColumn is a Column that wraps the data text of the column around.

    So a string that is to long for the column will be split into multiple lines in that column
    """
    def __init__(self, name, width, align, display_fn=unicode, expand=None):
        Column.__init__(self, name, width, align, display_fn, expand=expand)
        self._wrapper = textwrap.TextWrapper(width=self._width,
                                             expand_tabs=False,
                                             subsequent_indent=u"  "
                                             )

    def pack(self, data):
        """
        Packs the data for the column and if the data would be to long for the column
        it will be  split into multiple column lines.

        @param data the data that is packed

        @return an iteratable  with multiple column lines
        """
        return self._wrapper.wrap(self._display_fn(data))

    def set_width(self, width):
        Column.set_width(self, width)
        self._wrapper.width = self._width


class CutColumn(Column):
    """
    CutColumn is a Column that cuts of text that is greater then the Column.
    """
    def __init__(self, name, width, align, display_fn=unicode, expand=None):
        Column.__init__(self, name, width, align, display_fn, expand=expand)

    def pack(self, data):
        """
        Pack the data into the column and cut of everything that does not fir into the width.

        @param data the data that is packed
        """
        return (self._display_fn(data)[:self._width],)


def line_generator(columns, data):
    """
    Create a generator object which returns all lines of the View.

    @param columns the columns that are responsebile for printig the data
    @param data the data that will be turned into lines of text

    @returns a line generator
    """
    def next_line_iter(row_data):
        """
        Since a row can contain multiple lines we create the row and then return an iterator with all the lines.

        @param row_data the data for this row

        @returns the iterator for the lines of the rows
        """
        items = (column.pack(datum) for column, datum in zip(columns, row_data))
        return itertools.izip_longest(*items, fillvalue="")

    data_iter = iter(data)
    line_iter = next_line_iter(data_iter.next())
    while True:
        try:
            yield line_iter.next()
        except StopIteration:
            # ignore since we might have more in the data_iter
            pass

        # This breaks out of the loop when data_iter.next() throws a StopIteration
        line_iter = next_line_iter(data_iter.next())


class View(object):
    """
    View is an abstract class that defines the interface for a simple view.

    A view defines how events are displayed, therefor every view defines a
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self, width, columns):
        fixed_columns, expanding_columns = util.partition(lambda x: x.expand is None, columns)
        fix_size = sum((column.width for column in fixed_columns))
        expand_sum = sum(column.expand for column in expanding_columns)
        rest_size = max(0, width - fix_size - len(columns))
        for column in expanding_columns:
            column.set_width((rest_size * column.expand) // expand_sum)

        self._columns = columns
        header = []
        divider = []
        row_format = []
        for each in columns:
            header.append(("{:%s%d}" % ("^", each.width)).format(each.name))
            divider.append(u"─" * each.width)
            row_format.append("{:%s%d}" % (each.align, each.width))
        self._header = (u" ".join(header)) + u"\n" + (u"┼".join(divider))
        self._row_format = u"│".join(row_format)

    def print_view(self, store, args):
        """
        Print the view.

        @param store the Store object that holds the events
        @param args the arguments that define which events shall be selected
        """
        self.print_header()
        events = self._get_events(store, args)
        self._print_rows(self._get_data(events))

    def print_header(self):
        """ Print the header information of the view. """
        cli.util.uprint(self._header)

    def _print_row(self, event_data):
        """
        Print one row of the view.

        @param event_data the event that is displayed in that row
        """
        cli.util.uprint(self._row_format.format(*event_data))

    def _print_rows(self, data_list):
        """
        Print a list of event_data tuples.

        @param  data_list the events that will be printed in rows
        """
        for event_data in line_generator(self._columns, data_list):
            self._print_row(event_data)

    @abc.abstractmethod
    def _get_data(self, event):
        """
        Get the data for that row from the event.

        @event the event
        """
        raise NotImplementedError

    @abc.abstractmethod
    def _get_events(self, store, args):
        """
        Get the Events form the store object.

        @param store the Store object
        @param args the arguments of the cli
        """
        raise NotImplementedError


class TaskOverview(View):
    """
    An Overview for the tasks.
    """
    def __init__(self, config, width):
        date_printer = cli.printing.DatePrinter(config)
        columns = [CutColumn("ID", 4, "right"),
                   Column("S", 1, "center", cli.printing.state_to_symbol),
                   Column("D", 1, "center", cli.printing.diff_to_str),
                   Column("Due", date_printer.max_due_len, "center", date_printer.due_to_str),
                   WrapColumn("Title", 10, "left", expand=1)
                   ]
        View.__init__(self, width, columns)

    def _get_data(self, tasks):
        """
        Get the data for that row from the event.

        @event the event
        """
        return ((tsk.cache_id,
                 tsk.state,
                 tsk.difficulty,
                 tsk.due,
                 tsk.title
                 )
                for tsk in tasks)

    def _get_events(self, store, args):
        """
        Get the Events form the store object.

        @param store the Store object
        @param args the arguments of the cli
        """
        if args.all:
            return store.get_tasks(limit=-1)
        else:
            return store.get_open_tasks(limit=args.limit)


class ApmtOverview(View):
    """
    An Overview for the Appointments.
    """
    def __init__(self, config, width):
        date_printer = cli.printing.DatePrinter(config)
        columns = [CutColumn("ID", 4, "right"),
                   Column("Starts", date_printer.max_due_len + 4, "center", date_printer.due_to_str),
                   WrapColumn("Title", 10, "left", expand=1)
                   ]
        View.__init__(self, width, columns)

    def _get_data(self, apmts):
        """
        Get the data for that row from the event.

        @event the event
        """
        return ((apmt.cache_id,
                 apmt.schedule.start,
                 apmt.title
                 )
                for apmt in apmts)

    def _get_events(self, store, args):
        """
        Get the Events form the store object.

        @param store the Store object
        @param args the arguments of the cli
        """
        return store.get_apmts(task.now_with_tz(), datetime.timedelta(7, 0, 0))


class EventOverview(object):
    """
    The Overview of Tasks and Appointments.
    """
    def __init__(self, config, width):
        self.__head_line_format = "{:^%d}" % width
        self.__task_view = TaskOverview(config, width)
        self.__apmt_view = ApmtOverview(config, width)

    def _print_headline(self, head_line):
        """
        Print a separator for the different sub views.
        """
        cli.util.uprint(self.__head_line_format.format(head_line))

    def print_view(self, store, args):
        """
        Print the view.

        @param store the Store object that holds the events
        @param args the arguments that define which events shall be selected
        """
        self._print_headline("Appointments:")
        self.__apmt_view.print_view(store, args)
        self._print_headline("Tasks:")
        self.__task_view.print_view(store, args)

DEFAULT_VIEW = "overview"


VIEWS = {DEFAULT_VIEW: EventOverview,
         "tasks": TaskOverview,
         "apmts": ApmtOverview,
         }


def init_parser(subparsers):
    """Initialize the subparser of ls."""

    parser = subparsers.add_parser(COMMAND, help="list tasks.")
    parser.add_argument("view", type=cli.parser.to_unicode, default=DEFAULT_VIEW, nargs="?",
                        choices=VIEWS.keys())
    parser.add_argument("--all", action="store_true", help="list all tasks.")
    parser.add_argument("--limit", type=int, help="show a maximum of N tasks.", default=20)


def main(store, args, config, term):
    """
    List all open tasks.

    If args.all is given show all the tasks.

    """
    store.enable_caching()

    try:
        view = VIEWS[args.view](config, term.width if term.width else 80)
    except KeyError as excpt:
        cli.util.uprint("There is now view named \"%s\" \n\t Mhh this should not happen. \n\t(Error: %s)" % (args.view, excpt.message))
        return 1

    view.print_view(store, args)
    return 0

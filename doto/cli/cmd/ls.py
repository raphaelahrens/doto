"""
The command ls list all open tasks.

An example of its use is
    $ doto ls

"""
import datetime
import itertools
import textwrap

import doto.cli.parser
import doto.cli.printing
import doto.model
import doto.model.apmt
import doto.model.task


COMMAND = 'ls'
CONF_DEF = {}

APMT_LIMIT = datetime.timedelta(14, 0, 0)

uf = doto.cli.printing.UnicodeFormatter()


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
    def __init__(self, name, width, align, display_fn=str, expand=None):
        self._name = name
        self._width = width
        self._display_fn = display_fn
        self.__align = align
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

        This method can be called if the width of the column can be enlarged.

        If the parameter width is smaller then the member variable width, then this method has no effect

        @param width the new width
        """
        self._width = width if width > self._width else self._width


class WrapColumn(Column):
    """
    WrapColumn is a Column that wraps the data text of the column around.

    So a string that is to long for the column will be split into multiple lines in that column
    """

    newline_sym = ' ↩'
    len_nl_sy = len(newline_sym)

    def __init__(self, name, width, align, display_fn=str, expand=None):
        Column.__init__(self, name, width, align, display_fn, expand=expand)
        self._wrapper = textwrap.TextWrapper(width=self._width - WrapColumn.len_nl_sy,
                                             expand_tabs=False,
                                             subsequent_indent='  ')

    def add_newline_symbol(self, line):
        """ Adds a symbol to the line if the line is too long to fit """
        return uf.format('{:{align}{width}}{}', line, WrapColumn.newline_sym, align=self.align, width=self._wrapper.width)

    def pack(self, data):
        """
        Packs the data for the column and if the data would be to long for the column
        it will be  split into multiple column lines.

        @param data the data that is packed

        @return an iteratable  with multiple column lines
        """
        column_lines = self._wrapper.wrap(self._display_fn(data))
        return [self.add_newline_symbol(line) for line in column_lines[:-1]] + column_lines[-1:]

    def set_width(self, width):
        Column.set_width(self, width)
        self._wrapper.width = self._width - WrapColumn.len_nl_sy


class CutColumn(Column):
    """
    CutColumn is a Column that cuts of text that is greater then the Column.
    """
    def __init__(self, name, width, align, display_fn=str, expand=None):
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
        Since a row can contain multiple lines we create the row and then
        return an iterator with all the lines.

        @param row_data the data for this row

        @returns the iterator for the lines of the rows
        """
        items = (column.pack(datum) for column, datum in zip(columns, row_data))
        return itertools.zip_longest(*items, fillvalue='')

    data_iter = iter(data)
    line_iter = next_line_iter(next(data_iter))
    while True:
        try:
            yield next(line_iter)
        except StopIteration:
            # This breaks out of the loop when data_iter next throws a StopIteration
            line_iter = next_line_iter(next(data_iter))


class View(object):
    """
    View is an abstract class that defines the interface for a simple view.

    A view defines how events are displayed, therefore every view defines a
    """

    def __init__(self, width, columns):
        fixed_columns, expanding_columns = partition(lambda x: x.expand is None, columns)
        fix_size = sum((column.width for column in fixed_columns))
        expand_sum = sum(column.expand for column in expanding_columns)
        rest_size = max(0, width - fix_size - len(columns))
        for column in expanding_columns:
            column.set_width((rest_size * column.expand) // expand_sum)

        self._columns = columns
        header = []
        row_format = []
        for each in columns:
            header.append(uf.format('{:^%d}' % each.width, each.name))
            row_format.append('{:%s%d}' % (each.align, each.width))
        self._header = ' '.join(header)
        self._row_format = ' '.join(row_format)

    def print_view(self, store, args):
        """
        Print the view.

        @param store the Store object that holds the events
        @param args the arguments that define which events shall be selected
        """
        events = self.get_events(store, args)
        if len(events) > 0:
            store.add_to_cache(events)
            print(self._header)
            self._print_rows(self.get_column_data(events))

    def _print_row(self, event_data):
        """
        Print one row of the view.

        @param event_data the event that is displayed in that row
        """
        print(uf.format(self._row_format, *event_data))

    def _print_rows(self, data_list):
        """
        Print a list of event_data tuples.

        @param  data_list the events that will be printed in rows
        """
        for event_data in line_generator(self._columns, data_list):
            self._print_row(event_data)


class TaskOverview(View):
    """
    An Overview for the tasks.
    """
    def __init__(self, config, width):
        date_printer = doto.cli.printing.DatePrinter(config)
        columns = [CutColumn('I̲D̲', 4, '>'),
                   Column('D̲u̲e̲', date_printer.max_due_len, '>', date_printer.due_to_str),
                   Column(' ', 1, '^', doto.cli.printing.state_to_symbol),
                   Column(' ', 1, '^', doto.cli.printing.diff_to_str),
                   WrapColumn('T̲a̲s̲k̲ ̲t̲i̲t̲l̲e̲', 10, '<', expand=1)
                   ]
        View.__init__(self, width, columns)

    def get_column_data(self, tasks):
        """
        Get the data for that row from the event.

        @event the event
        """
        return ((tsk.cache_id,
                 tsk.due,
                 tsk.state,
                 tsk.difficulty,
                 tsk.title
                 )
                for tsk in tasks)

    def get_events(self, store, args):
        """
        Get the Events form the store object.

        @param store the Store object
        @param args the arguments of the CLI
        """
        if args.all:
            return doto.model.task.get_open_tasks(store, limit=None)
        else:
            return doto.model.task.get_open_tasks(store, limit=args.limit)


class ApmtOverview(View):
    """
    An Overview for the Appointments.
    """
    def __init__(self, config, width):
        date_printer = doto.cli.printing.DatePrinter(config)
        columns = [CutColumn('I̲D̲', 4, '>'),
                   Column('S̲t̲a̲r̲t̲s̲ ̲i̲n̲', date_printer.max_due_len, '^', date_printer.due_to_str),
                   Column(' ', 8, '<'),
                   WrapColumn('A̲p̲p̲o̲i̲n̲t̲m̲e̲n̲t̲ ̲t̲i̲t̲l̲e̲', 10, '<', expand=1)
                   ]
        View.__init__(self, width, columns)

    def get_column_data(self, apmts):
        """
        Get the data for that row from the event.

        @event the event
        """
        return ((apmt.cache_id,
                 apmt.schedule.start,
                 apmt.repeat,
                 apmt.title
                 )
                for apmt in apmts)

    def get_events(self, store, args):
        """
        Get the Events form the store object.

        @param store the Store object
        @param args the arguments of the CLI
        """
        if args.all:
            apmts = doto.model.apmt.get_all(store, doto.model.now_with_tz())
        else:
            apmts = doto.model.apmt.get_current(store, doto.model.now_with_tz(), APMT_LIMIT)
        return apmts


class EventOverview(object):
    """
    The Overview of Tasks and Appointments.
    """
    def __init__(self, config, width):
        self.__head_line_format = '{:^%d}' % width
        self.__task_view = TaskOverview(config, width)
        self.__apmt_view = ApmtOverview(config, width)

    def print_view(self, store, args):
        """
        Print the view.

        @param store the Store object that holds the events
        @param args the arguments that define which events shall be selected
        """
        self.__apmt_view.print_view(store, args)
        print()
        self.__task_view.print_view(store, args)

DEFAULT_VIEW = 'overview'


VIEWS = {DEFAULT_VIEW: EventOverview,
         'tasks': TaskOverview,
         'apmts': ApmtOverview,
         }


def init_parser(subparsers):
    """Initialize the subparser of ls."""

    parser = subparsers.add_parser(COMMAND, help='list tasks.')
    parser.add_argument('view', type=str, default=DEFAULT_VIEW, nargs='?',
                        choices=VIEWS.keys())
    parser.add_argument('--all', action='store_true', help='list all tasks.')
    parser.add_argument('--limit', type=int, help='show a maximum of N tasks.', default=20)


def main(store, args, config, term):
    """
    List all open tasks.

    If args.all is given show all the tasks.

    """

    try:
        view = VIEWS[args.view](config, term.columns if term.columns else 80)
    except KeyError:
        print('There is now view named "{}"\n\tMhh this should not happen.'.format(args.view))
        return 1

    view.print_view(store, args)
    store.save()
    return 0

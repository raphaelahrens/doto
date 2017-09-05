# -*- coding: utf-8 -*-
"""
The command "show" can be used to delete task from the Done!Tools store.

An example of its use would be
    $ doto del 10

"""
import doto.cli.util
import doto.cli.printing

COMMAND = "show"
CONF_DEF = {}


def init_parser(subparsers):
    """ Initialize the subparser. """
    parser = subparsers.add_parser(COMMAND, help="delete a task from the list.")
    parser.add_argument("id", type=int, nargs='?', default=-1, help="the id of the task which should be deleted.")


def schedule_to_str(schedule, date_printer):
    start = date_printer.date_to_str(schedule.start)
    if schedule.end is not None:
        end = date_printer.date_to_str(schedule.end)
        return '{start}--{end}'.format(start=start, end=end)
    else:
        return '{start}'.format(start=start)


class Row(object):
    def __init__(self, title, value, *, fmt_str='{}'):
        self.fmt_str = fmt_str
        self.title = title
        self.value = value

    def print_row(self, width):
        return self.fmt_str.format(self.title, self.value, width=width)


class SplitRow(object):
    def __init__(self, columns):
        self.columns = columns

    def print_row(self, width):
        n_columns = len(self.columns)
        split_width = max(0, (width // n_columns) - 2)

        def cut(string):
            return string[:split_width]
        title_fmt = ' {:^{width}} ' * n_columns
        value_fmt = ' {:^{width}} ' * n_columns
        titles, values = zip(*((cut(c.title), cut(c.value)) for c in self.columns))

        title_str = title_fmt.format(*titles, width=split_width)
        value_str = value_fmt.format(*values, width=split_width)
        return '\n'.join((title_str, value_str))


def show(apmt, width, date_printer):
    ''' Show the given Appointment in a given width
    @param: apmt a object of type Appointment
    @param: width an int
    @param: config the configuration
    '''
    title = Row('Title', apmt.title, fmt_str='{}: {}\n')
    description = Row('Description', apmt.description, fmt_str='{}:\n {}\n')
    schedule = Row('Schedule', schedule_to_str(apmt.schedule, date_printer))
    created = Row('Created', date_printer.date_to_str(apmt.created))

    repeat = Row('Repeat', str(apmt.repeat)) if apmt.repeat else Row('', '')

    merged = SplitRow((schedule, repeat, created))

    layout = [title]
    if apmt.description:
        layout.append(description)

    layout.append(merged)

    for row in layout:
        print(row.print_row(width))


def main(store, args, config, term):
    """ Delete the given task in args.id. """

    apmt, error = doto.cli.cmd.apmt.get_cached_apmt(store, args.id)
    if not apmt:
        return error
    width = term.columns if term.columns else 80
    date_printer = doto.cli.printing.DatePrinter(config)
    show(apmt, width, date_printer)

    return 0

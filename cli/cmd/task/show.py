# -*- coding: utf-8 -*-
"""
The command "show" can be used to delete task from the Done!Tools store.

An example of its use would be
    $ doto del 10

"""
import cli.printing

COMMAND = "show"
CONF_DEF = {}


def init_parser(subparsers):
    """ Initialize the subparser. """
    parser = subparsers.add_parser(COMMAND, help="delete a task from the list.")
    parser.add_argument("id", type=int, help="the id of the task which should be deleted.")


class TaskPrinter(object):
    def __init__(self, config):
        self.__date_printer = cli.printing.DatePrinter(config)

    def show(self, tsk, width):
        title_header = "Title"

        state_header = "State"

        state_str = cli.printing.state_to_str(tsk.state)
        state_sym = cli.printing.state_to_symbol(tsk.state)

        headline_format = "{}: {:>{fill_width}}:{:>{state_width}}{}\n  {}\n"

        state_width = 10

        headline_width = max(0, width - len(title_header) - len(state_header) - state_width)

        print(headline_format.format(title_header,
                                     state_header,
                                     state_str,
                                     state_sym,
                                     tsk.title,
                                     fill_width=headline_width,
                                     state_width=state_width
                                     )
              )
        print("Description:\n {}\n".format(tsk.description))
        date_width = max(0, (width - 2) / 2)
        date_format = "{:^{date_width}}  {:^{date_width}}"
        print(date_format.format("Created:",
                                 "Due:",
                                 date_width=date_width
                                 )
              )
        print(date_format.format(self.__date_printer.date_to_str(tsk.created),
                                 self.__date_printer.due_to_str(tsk.due, default="--"),
                                 date_width=date_width
                                 )
              )


def main(store, args, config, term):
    """ Delete the given task in args.id. """

    tsk, error = cli.cmd.task.get_cached_task(store, args.id)
    if not tsk:
        return error

    TaskPrinter(config).show(tsk, term.width if term.width else 80)

    return 0

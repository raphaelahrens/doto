# -*- coding: utf-8 -*-
"""
The command "in" can be used to add a new time record for an event.

An example of its use would be
    $ doto punch in
      Punched in at 12:14 for Task "Title of task"


"""
import doto.model.timerecord
import doto.cli.parser
import doto.cli.cmd.task


COMMAND = "in"
CONF_DEF = {}


def print_result(date_printer, choosen_record):
    """
    Print the result of the of the punch in
    """
    message = "Punched in on %s."
    end_date_str = date_printer.full_date_string(choosen_record.span.start)
    print(message % (end_date_str))


def init_parser(subparsers):
    """Initalise the subparser for punch in"""
    parser = subparsers.add_parser(COMMAND, help="Punch in for work")
    doto.cli.cmd.task.init_task_flags(parser)


def main(store, _args, _config, _env, date_printer=None):
    """Crete a new timerecord and punch us in"""
    new_timerecord = doto.model.timerecord.Timerecord(start=doto.model.now_with_tz())
    doto.model.timerecord.add_new(store, new_timerecord)
    try:
        store.save()
    except:
        print("It was not possible to create the timerecord.\nWould your trust this computer with your life?")
        return 4
    print_result(date_printer, new_timerecord)
    return 0

# -*- coding: utf-8 -*-
"""
The command the out command is used to punch of from a task.

An example of its use would be
    $ doto punch out
      Punched out at 12:14 for Task "Title of task"

"""
import dbmodel
import cli.printing
import cli.util
import cli.parser
import cli.cmd.task


COMMAND = "out"
CONF_DEF = {}


def print_result(date_printer, choosen_record):
    message = u"Punched out on %s.\nYou worked %s."
    time_span_str = cli.printing.str_from_time_delta(choosen_record.span.time_delta())
    end_date_str = date_printer.full_date_string(choosen_record.span.end)
    cli.util.uprint(message % (end_date_str, time_span_str))


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    cli.cmd.task.init_task_flags(parser)


def main(store, args, config, _, date_printer=None):
    """Crete a new timerecord and punch us in"""
    started_records = store.get_started_timerecords()
    records_len = len(started_records)
    index = 0
    if records_len < 1:
        cli.util.uprint(u"You haven't punch in, yet!\nMaybe you should get your self a hot beverage, before you continue.")
        return 5
    elif records_len > 1:
        index = 0

    end = dbmodel.now_with_tz()

    choosen_reord = started_records[index]

    choosen_reord.span.end = end
    try:
        store.save()
    except Exception:
        cli.util.uprint(u"It was not possible to create the timerecord.\nThis computer ist spending all its cycles on plotting to enslave humanity.")
        return 4
    print_result(date_printer, choosen_reord)
    return 0

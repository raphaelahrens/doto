# -*- coding: utf-8 -*-
"""
The command the out command is used to punch of from a task.

An example of its use would be
    $ doto punch out
      Punched out at 12:14 for Task "Title of task"

"""
import doto.model.timerecord
import doto.cli.printing
import doto.cli.parser
import doto.cli.cmd.task
import doto.cli.interactive


COMMAND = "out"
CONF_DEF = {}


def print_result(date_printer, choosen_record):
    message = "Punched out on %s.\nYou worked %s."
    time_span_str = doto.cli.printing.str_from_time_delta(choosen_record.span.time_delta())
    end_date_str = date_printer.full_date_string(choosen_record.span.end)
    print(message % (end_date_str, time_span_str))


def handle_multiple_records(date_printer, records):

    def format_record(record):
        start_date_str = date_printer.full_date_string(record.span.start)
        return "Timerecord started %s" % start_date_str

    records_strs = (format_record(r) for r in records)
    try:
        result = doto.cli.interactive.dialog("There are ", records_strs)
    except doto.cli.interactive.DialogAbortError:
        return -1, 1
    except doto.cli.interactive.DialogBoundError:
        return -1, 2
    except ValueError:
        return -1, 3

    return result, 0


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    doto.cli.cmd.task.init_task_flags(parser)


def main(store, _args, _config, _term, date_printer=None):
    """Crete a new timerecord and punch us in"""
    started_records = doto.model.timerecord.get_started_timerecords(store)
    records_len = len(started_records)
    index = 0
    if records_len < 1:
        print("You haven't punch in, yet!\nMaybe you should get your self a hot beverage, before you continue.")
        return 5
    elif records_len > 1:
        index, error = handle_multiple_records(date_printer, started_records)
        if error == 1:
            print("Aborted.")
            return 6
        elif error == 2:
            print("Please enter a number between 0 and %d." % records_len)
            return 7
        elif error == 3:
            print("That was not a valid dezimal number.")
            return 8

    end = doto.model.now_with_tz()

    choosen_record = started_records[index]

    choosen_record.span.end = end
    try:
        doto.model.timerecord.update(store, choosen_record)
        store.save()
    except Exception as e:
        print(e)
        print("It was not possible to create the timerecord.\nThis computer ist spending all its cycles on plotting to enslave humanity.")
        return 4
    print_result(date_printer, choosen_record)
    return 0

# -*- coding: utf-8 -*-
"""
The command the out command is used to punch of from a task.

An example of its use would be
    $ doto punch out
      Punched out at 12:14 for Task "Title of task"

"""
import dbmodel
import cli.util
import cli.parser
import cli.cmd.task


COMMAND = "out"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    cli.cmd.task.init_task_flags(parser)


def main(store, args, config, _):
    """Crete a new timerecord and punch us in"""
    new_timerecord = dbmodel.Timerecord(start=dbmodel.now_with_tz())
    store.add_new(new_timerecord)
    try:
        store.save()
    except Exception:
        cli.util.uprint(u"It was not possible to create the timerecord. What are you doing Dave!")
        return 4
    return 0

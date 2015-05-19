# -*- coding: utf-8 -*-
"""
The command "in" can be used to add a new time record for an event.

An example of its use would be
    $ doto punch in
      Punched in at 12:14 for Task "Title of task"


"""
import dbmodel
import cli.util
import cli.parser
import cli.cmd.task


COMMAND = "in"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for punch in"""
    parser = subparsers.add_parser(COMMAND, help="Punch in for work")
    cli.cmd.task.init_task_flags(parser)


def main(store, args, config, _):
    """Crete a new timerecord and punch us in"""
    new_timerecord = dbmodel.Timerecord(start=dbmodel.now_with_tz())
    store.add_new(new_timerecord)
    try:
        store.save()
    except Exception, e:
        cli.util.uprint(e.message)
        cli.util.uprint(u"It was not possible to create the timerecord. What are you doing Dave!")
        return 4
    cli.util.uprint(u"Punched in at %s for Task \"%s\"" % (new_timerecord.span.start, "TEST"))
    return 0

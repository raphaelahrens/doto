# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
    $ doto done id

"""
import cli


COMMAND = "start"
CONF_DEF = {}


def init_parser(subparsers):
    """ Init the arg parser. """
    cli.parser.init_id_flag(COMMAND, subparsers)


def main(store, args, *_):
    """ The Main method of start."""
    start_task, error = cli.util.get_cached_task(store, args.id)
    if not start_task:
        return error
    print "CLI START"
    if not start_task.start():
        cli.util.uprint(("The task with the Id: " + cli.util.ID_FORMAT + "was already started!") % (args.id, start_task.event_id))
        return 5

    try:
        store.save()
    except:
        cli.util.uprint(("It was not possible to finish the task with id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, start_task.event_id))
        return 4

    cli.util.uprint(("You started :\n\t(" + cli.util.ID_FORMAT + ") %s") % (args.id, start_task.event_id, start_task.title))
    return 0

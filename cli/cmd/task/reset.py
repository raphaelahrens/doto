# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
    $ doto done id

"""
import cli


COMMAND = "reset"
CONF_DEF = {}


def init_parser(subparsers):
    """ Init the arg parser. """
    cli.parser.init_id_flag(COMMAND, subparsers)


def main(store, args, *_):
    """ The Main method of start."""
    start_task, error = cli.cmd.task.get_cached_task(store, args.id)
    if not start_task:
        return error
    start_task.reset()
    try:
        store.save()
    except:
        print(("It was not possible to finish the task with id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, start_task.event_id))
        return 4

    print(("Reseted the state of :\n\t(" + cli.util.ID_FORMAT + ") %s") % (args.id, start_task.event_id, start_task.title))
    return 0

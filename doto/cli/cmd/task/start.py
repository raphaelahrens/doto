# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
    $ doto done id

"""
import doto.cli


COMMAND = "start"
CONF_DEF = {}


def init_parser(subparsers):
    """ Init the arg parser. """
    doto.cli.parser.init_id_flag(COMMAND, subparsers)


def main(store, args, *_):
    """ The Main method of start."""
    start_task, error = doto.cli.cmd.task.get_cached_task(store, args.id)
    if not start_task:
        return error

    if not start_task.start():
        print(("The task with the Id: " + doto.cli.util.ID_FORMAT + "was already started!") % (args.id, start_task.event_id))
        return 5

    try:
        store.save()
    except Exception as excpt:
        print(("It was not possible to finish the task with id "
               + doto.cli.util.ID_FORMAT
               + ":\n\t %r \n\t(Error: %s)")
              % (args.id, start_task.event_id, excpt.message))
        return 4

    print(("You started :\n\t(" + doto.cli.util.ID_FORMAT + ") %s") % (args.id, start_task.event_id, start_task.title))
    return 0

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
    tsk, error = doto.cli.cmd.task.get_cached_task(store, args.id)
    if not tsk:
        return error

    if not tsk.start():
        print(("The task with the Id: " + doto.cli.util.ID_FORMAT + "was already started!") % (args.id, tsk.id))
        return 5

    try:
        doto.model.task.update(store, tsk)
        store.save()
    except Exception as excpt:
        print(("It was not possible to finish the task with id "
               + doto.cli.util.ID_FORMAT
               + ":\n\t %r \n\t(Error: %s)")
              % (args.id, tsk.id, excpt.message))
        return 4

    print(("You started :\n\t(" + doto.cli.util.ID_FORMAT + ") %s") % (args.id, tsk.id, tsk.title))
    return 0

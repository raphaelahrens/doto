# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
    $ doto done id

"""
import doto.cli


COMMAND = "reset"
CONF_DEF = {}


def init_parser(subparsers):
    """ Init the arg parser. """
    doto.cli.parser.init_id_flag(COMMAND, subparsers)


def main(store, args, *_):
    """ The Main method of start."""
    tsk, error = doto.cli.cmd.task.get_cached_task(store, args.id)
    if not tsk:
        return error
    tsk.reset()
    try:
        doto.model.task.update(store, tsk)
        store.save()
    except:
        print(("It was not possible to finish the task with id " + doto.cli.util.ID_FORMAT + ":\n\t %r") % (args.id, tsk.id))
        return 4

    print(("Reseted the state of :\n\t(" + doto.cli.util.ID_FORMAT + ") %s") % (args.id, tsk.id, tsk.title))
    return 0

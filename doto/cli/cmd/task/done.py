# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
    $ doto done id

"""
import doto.cli.util
import doto.cli.cmd.task


COMMAND = "done"
CONF_DEF = {}


def init_parser(subparsers):
    """
    Init the parser

    It adds the id argument to the argument parser
    """
    parser = subparsers.add_parser(COMMAND, help="")
    parser.add_argument("id", type=int, help="the id of the task which should be finished.")


def main(store, args, *_):
    """ The Main method of done."""
    tsk, error = doto.cli.cmd.task.get_cached_task(store, args.id)
    if not tsk:
        return error
    if not tsk.done():
        print(("The task with the Id: " + doto.cli.util.ID_FORMAT + "was already finished!") % (args.id, tsk.id))
        return 5
    try:
        doto.model.task.update(store, tsk)
        store.save()
    except:
        print(("It was not possible to finish the task with id " + doto.cli.util.ID_FORMAT + ":\n\t %r") % (args.id, tsk.id))
        return 4

    print(("Good you finished:\n\t(" + doto.cli.util.ID_FORMAT + ") %s") % (args.id, tsk.id, tsk.title))
    return 0

# -*- coding: utf-8 -*-
"""
The command "del" can be used to delete task from the Done!Tools store.

An example of its use would be
    $ doto del 10

"""
import doto.cli.util
import doto.cli.cmd.task

COMMAND = "del"
CONF_DEF = {}


def init_parser(subparsers):
    """ Initialize the subparser. """
    parser = subparsers.add_parser(COMMAND, help="delete a task from the list.")
    parser.add_argument("id", type=int, help="the id of the task which should be deleted.")


def main(store, args, *_):
    """ Delete the given task in args.id. """

    tsk, error = doto.cli.cmd.task.get_cached_task(store, args.id)
    if not tsk:
        return error
    try:
        doto.model.task.delete(store, tsk)
        store.save()
    except:
        print(("It was not possible to delete the task with the id " + doto.cli.util.ID_FORMAT + ":\n\t %r") % (args.id, tsk.id))
        return 4

    print(("Deleted event with id " + doto.cli.util.ID_FORMAT + ":\n\t Title: %s") % (args.id, tsk.id, tsk.title))
    return 0

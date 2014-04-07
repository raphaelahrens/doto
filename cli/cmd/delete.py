# -*- coding: utf-8 -*-
"""
The command "del" can be used to delete task from the Done!Tools store.

An example of its use would be
    $ doto del 10

"""
import cli.util

COMMAND = "del"
CONF_DEF = {}


def init_parser(subparsers):
    """ Initialize the subparser. """
    parser = subparsers.add_parser(COMMAND, help="delete a task from the list.")
    parser.add_argument("id", type=int, help="the id of the task which should be deleted.")


def main(store, args, config, term):
    """ Delete the given task in args.id. """

    del_task, error = cli.util.get_cached_task(store, args.id)
    if not del_task:
        return error
    store.delete(del_task)
    if not store.save():
        cli.util.uprint(("It was not possible to delete the task with the id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, del_task))
        return 4

    cli.util.uprint(("Deleted task with id " + cli.util.ID_FORMAT + ":\n\t Title: %s") % (args.id, del_task.task_id, del_task.title))
    return 0

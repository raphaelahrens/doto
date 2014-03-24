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


def main(store, args, config):
    """ Delete the given task in args.id. """
    cache = store.get_cache()
    if not cache:
        tasks = store.get_tasks()
        if tasks:
            cli.util.uprint("I don't know what you want to delete!\nYou should first run:\n\tdoto ls")
            return 3
        cli.util.uprint("There are no tasks.\nMaybe you would first like to add a new task with: \n\t doto add \"title\" \"description\" ")
        return 2

    if args.id not in cache:
        cli.util.uprint("There is no task with the id %d" % args.id)
        return 1

    del_task = cache[args.id]
    store.delete(del_task)
    if not store.save():
        cli.util.uprint("It was not possible to delete the task with the id " + cli.util.ID_FORMAT + ":\n\t %r" % (args.id, del_task))
        return 4

    cli.util.uprint("Deleted task with id " + cli.util.ID_FORMAT + ":\n\t Title: %s" % (args.id, del_task.task_id, del_task.title))
    return 0

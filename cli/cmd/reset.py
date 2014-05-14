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
    """
    Init the parser

    It adds the id argument to the argument parser
    """
    parser = subparsers.add_parser(COMMAND, help="")
    parser.add_argument("id", type=int, help="the id of the task which should be finished.")


def main(store, args, config, term):
    """ The Main method of start."""
    start_task, error = cli.util.get_cached_task(store, args.id)
    if not start_task:
        return error
    start_task.reset()
    store.modify(start_task)
    if not store.save():
        cli.util.uprint(("It was not possible to finish the task with id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, start_task.task_id))
        return 4

    cli.util.uprint(("Reseted the state of :\n\t(" + cli.util.ID_FORMAT + ") %s") % (args.id, start_task.task_id, start_task.title))
    return 0

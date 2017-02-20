# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
    $ doto done id

"""
import cli.util
import cli.cmd.task


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
    done_task, error = cli.cmd.task.get_cached_task(store, args.id)
    if not done_task:
        return error
    if not done_task.done():
        print(("The task with the Id: " + cli.util.ID_FORMAT + "was already finished!") % (args.id, done_task.event_id))
        return 5
    try:
        store.save()
    except:
        print(("It was not possible to finish the task with id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, done_task.event_id))
        return 4

    print(("Good you finished:\n\t(" + cli.util.ID_FORMAT + ") %s") % (args.id, done_task.event_id, done_task.title))
    return 0

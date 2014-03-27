# -*- coding: utf-8 -*-
"""
The command "add" can be used to add a new task to Done!Tools

An example of its use would be
    $ doto add "Document the Add command" "Add still has no doc strings" --difficulty 1

"""
import task
import cli.util


COMMAND = "add"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    parser.add_argument("title", type=cli.util.to_unicode, help="The title of the new task")
    parser.add_argument("description", type=cli.util.to_unicode, help=" of the new task")
    parser.add_argument("--due", type=cli.util.to_unicode, help="the estimated completion date.")
    parser.add_argument("--difficulty", type=int, choices=task.DIFFICULTY.keys, help="the estimated difficulty of the task.")


def main(store, args, config):
    """Add a new task with the given args"""
    tsk = task.Task(args.title, args.description)
    if args.due is not None:
        tsk.schedule.due = task.Date.local_from_str(args.due, config.date.cli_input_str)
    store.add_new(tsk)
    store.save()
    return 0

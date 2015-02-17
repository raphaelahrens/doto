# -*- coding: utf-8 -*-
"""
The command "add" can be used to add a new task to Done!Tools

An example of its use would be
    $ doto add "Document the Add command" "Add still has no doc strings" --difficulty 1

"""
import dbmodel
import cli.util
import cli.parser
import cli.cmd.task


COMMAND = "add"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    parser.add_argument("title", type=cli.parser.to_unicode, help="The title of the new task")
    parser.add_argument("description", type=cli.parser.to_unicode, help="The description of the new task")
    cli.cmd.task.init_task_flags(parser)


def main(store, args, config, _):
    """Add a new task with the given args"""
    new_task = dbmodel.Task(args.title, args.description)
    if args.due is not None:
        new_task.due = cli.parser.date_parser(args.due)
    if args.difficulty is not None:
        new_task.difficulty = args.difficulty
    store.add_new(new_task)
    try:
        store.save()
    except Exception:
        cli.util.uprint(u"It was not possible to save the new task. What are you doing Dave!")
        return 4
    return 0

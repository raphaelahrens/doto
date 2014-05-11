# -*- coding: utf-8 -*-
"""
The command "add" can be used to add a new task to Done!Tools

An example of its use would be
    $ doto add "Document the Add command" "Add still has no doc strings" --difficulty 1

"""
import task
import cli.util
import cli.parser


COMMAND = "add"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    parser.add_argument("title", type=cli.util.to_unicode, help="The title of the new task")
    parser.add_argument("description", type=cli.util.to_unicode, help="The description of the new task")
    cli.parser.init_task_flags(parser)


def main(store, args, config, term):
    """Add a new task with the given args"""
    new_task = task.Task(args.title, args.description)
    if args.due is not None:
        new_task.schedule.due = task.Date.local_from_str(args.due, config.date.cli_input_str)
    if args.difficulty is not None:
        new_task.difficulty = args.difficulty
    store.add_new(new_task)
    if not store.save():
        cli.util.uprint(("It was not possible to save the new task with id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, new_task.task_id))
        return 4
    return 0

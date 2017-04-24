# -*- coding: utf-8 -*-
"""
The command "add" can be used to add a new task to Done!Tools

An example of its use would be
    $ doto add "Document the Add command" "Add still has no doc strings" --difficulty 1

"""
import doto.model.task
import doto.cli.parser
import doto.cli.cmd.task


COMMAND = "add"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    parser.add_argument("title", type=str, help="The title of the new task")
    parser.add_argument("description", type=str, help="The description of the new task")
    doto.cli.cmd.task.init_task_flags(parser)


def main(store, args, _config, _env):
    """Add a new task with the given args"""
    tsk = doto.model.task.Task(args.title, args.description)
    if args.due is not None:
        tsk.due = doto.cli.parser.date_parser(args.due)
    tsk.repeat = args.repeat
    if args.difficulty is not None:
        tsk.difficulty = args.difficulty
    try:
        doto.model.task.add_new(store, tsk)
        store.save()
    except:
        print("It was not possible to save the new task. What are you doing Dave!")
        return 4
    return 0

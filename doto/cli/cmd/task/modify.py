# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
$ doto modify id  [--title <string>] [--description <string>]  [--due <date>]  [--difficulty <int>]

"""
import doto.cli.parser
import doto.cli.util
import doto.cli.cmd.task


COMMAND = "modify"
CONF_DEF = {}

RESET = "RESET"


def init_parser(subparsers):
    """
    Init the parser

    It adds the id argument to the argument parser
    """
    parser = subparsers.add_parser(COMMAND, help="")
    parser.add_argument("id", type=int, help="The id of the task which should be modified.")
    parser.add_argument("--title", type=doto.cli.parser.to_unicode, help="Change the title of the task")
    parser.add_argument("--description", type=doto.cli.parser.to_unicode, help="Change the description of the task")
    doto.cli.cmd.task.init_task_flags(parser)


def set_or_reset(value, fnc=lambda x: x):
    """
    Check if a value is should be set or reset

    If the given value is equal to "RESET" the set the value to None
    else use the function fnc to set it to the return value of fnc.

    @param value the value that schould be tested
    @param fnc a function that can be used to convert the value. Default=identity function
    """
    if value == RESET:
        return None
    return fnc(value)


def main(store, args, _config, _env):
    """ The Main method of start."""

    tsk, error = doto.cli.cmd.task.get_cached_task(store, args.id)
    if not tsk:
        return error
    print(("Changing task " + doto.cli.util.ID_FORMAT + ":\n\t %s") % (args.id, tsk.id, tsk.title))
    if args.title is not None:
        tsk.title = args.title
    if args.description is not None:
        tsk.description = args.description
    if args.due is not None:
        tsk.due = set_or_reset(args.due, doto.cli.parser.date_parser)
    if args.difficulty is not None:
        tsk.difficulty = args.difficulty

    try:
        doto.model.task.update(store, tsk)
        store.save()
    except:
        print(("It was not possible to modify the task with id " + doto.cli.util.ID_FORMAT + ":\n\t %r") % (args.id, tsk.id))
        return 4

    print(("You modified:\n\t(" + doto.cli.util.ID_FORMAT + ") %s") % (args.id, tsk.id, tsk.title))
    return 0

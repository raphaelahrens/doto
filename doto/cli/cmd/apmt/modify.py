# -*- coding: utf-8 -*-
"""
The command

An example of its use would be
$ doto apmt modify id  [--title <string>] [--description <string>]  [--due <date>]  [--difficulty <int>]

"""
import doto.cli


COMMAND = "modify"
CONF_DEF = {}

RESET = "RESET"


def init_parser(subparsers):
    """
    Init the parser

    It adds the id argument to the argument parser
    """
    parser = subparsers.add_parser(COMMAND, help="")
    parser.add_argument("id", type=int, help="The id of the appointment which should be modified.")
    parser.add_argument("--title", type=str, help="The title of the new appointment")
    parser.add_argument("--start", type=str, help="The date when the new appointment will start")
    doto.cli.cmd.apmt.init_apmt_flags(parser)


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

    modify_task, error = doto.cli.util.get_cached_task(store, args.id)
    if not modify_task:
        return error
    print(("Changing task " + doto.cli.util.ID_FORMAT + ":\n\t %s") % (args.id, modify_task.id, modify_task.title))
    if args.title is not None:
        modify_task.title = args.title
    if args.description is not None:
        modify_task.description = args.description
    if args.start is not None:
        modify_task.start = set_or_reset(args.start, doto.cli.parser.date_parser)
    if args.difficulty is not None:
        modify_task.difficulty = args.difficulty

    try:
        store.save()
    except:
        print(("It was not possible to modify the task with id " + doto.cli.util.ID_FORMAT + ":\n\t %r") % (args.id, modify_task.id))
        return 4

    print(("You modified:\n\t(" + doto.cli.util.ID_FORMAT + ") %s") % (args.id, modify_task.id, modify_task.title))
    return 0

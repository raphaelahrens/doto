# -*- coding: utf-8 -*-
"""
The command "add" can be used to add a new task to Done!Tools

An example of its use would be
    $ doto add "Document the Add command" "Add still has no doc strings" --difficulty 1

"""
import task
import cli.util


COMMAND = "apmt"
CONF_DEF = {}


def init_parser(subparsers):
    """Initalise the subparser for Add"""
    parser = subparsers.add_parser(COMMAND, help="Add a new task to the task list")
    parser.add_argument("title", type=cli.util.to_unicode, help="The title of the new appointment")
    parser.add_argument("start", type=cli.util.to_unicode, help="The date when the new appointment will start")
    parser.add_argument("--description", type=cli.util.to_unicode, help="The description of the new task")
    parser.add_argument("--end", type=cli.util.to_unicode, help="The date when the new appointment will end")


def main(store, args, config, _):
    """Add a new task with the given args"""
    start = task.Date.local_from_str(args.start, config.date.cli_input_str)
    new_apmt = task.Appointment(args.title, start)
    if args.end is not None:
        new_apmt.schedule.end = task.Date.local_from_str(args.end, config.date.cli_input_str)
    if args.description is not None:
        new_apmt.description = args.description
    store.add_new(new_apmt)
    if not store.save():
        cli.util.uprint(("It was not possible to save the new task with id "
                         + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, new_apmt.event_id))
        return 4
    return 0

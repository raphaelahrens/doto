# -*- coding: utf-8 -*-
"""
The command ls list all open tasks.

An example of its use is
    $ doto ls

"""
import cli.util


COMMAND = "ls"
CONF_DEF = {}


def init_parser(subparsers):
    """Initialize the subparser of ls."""
    parser = subparsers.add_parser(COMMAND, help="list tasks.")
    parser.add_argument("--all", action="store_true", help="list all tasks.")


def extract_task_data(tsk, config):
    """
    Create a tuple with all the values that shall be printed in the new table

    @param tsk the task that will be printed
    @param config the configuration
    """
    return (tsk.task_id,
            tsk.title,
            tsk.difficulty,
            "" if tsk.due is None else tsk.due.local_str(config.date.cli_out_str))


def main(store, args, config):
    """
    List all open tasks.

    If args.all is given show all the tasks.

    """
    tasks = store.get_tasks()
    headers = [("ID", 4), ("Title", 20), ("Diff", 4), ("Due", 15)]

    cli.util.print_table(headers, [extract_task_data(tsk, config) for tsk in tasks])

    store.close()

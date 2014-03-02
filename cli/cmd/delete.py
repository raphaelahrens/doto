# -*- coding: utf-8 -*-
"""
The command "del" can be used to delete task from the Done!Tools store.

An example of its use would be
    $ doto del 10

"""
import cli.util

COMMAND = "del"
CONF_DEF = {}


def init_parser(subparsers):
    """ Inituialize the subparser. """
    parser = subparsers.add_parser(COMMAND, help="delete a task from the list.")
    parser.add_argument("id", type=int, help="the id of the task which should be deleted.")


def main(store, args, config):
    """ Delete the given task in args.id. """
    cli.util.uprint("try to delete")

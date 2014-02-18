# -*- coding: utf-8 -*-
import cli.util

COMMAND = "del"


def init_parser(subparsers):
    parser = subparsers.add_parser(COMMAND, help="delete a task from the list.")
    parser.add_argument("id", type=int, help="the id of the task which should be deleted.")


def main(store, args):
    cli.util.uprint("try to delete")

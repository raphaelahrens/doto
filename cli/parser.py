# -*- coding: utf-8 -*-
"""
This module holds a common parser for the add and modify command.
"""
import cli
import task
import pytz
import datetime


def init_task_flags(parser):
    """
    Set the Flags for creating or modifing a task
    """
    # parser.add_argument("--category", type=cli.util.to_unicode, help="Set the category of this task.")
    # parser.add_argument("--planned-end", type=cli.util.to_unicode, help="The scheduled end of the task.")
    # parser.add_argument("--planned-start", type=cli.util.to_unicode, help="The scheduled start of the task.")
    # parser.add_argument("--project", type=cli.util.to_unicode, help="Set the project of this task.")
    parser.add_argument("--difficulty", type=int, choices=task.DIFFICULTY.keys, help="the estimated difficulty of the task.")
    parser.add_argument("--due", type=cli.util.to_unicode, help="the estimated completion date.")


def init_id_flag(command, subparser):
    """
    Init the parser

    It adds the id argument to the argument parser
    """
    parser = subparser.add_parser(command, help="")
    parser.add_argument("id", type=int, help="the id of the task which should be finished.")


def set_date_parser(local_tz_str, format_str):
    local_tz = pytz.timezone(local_tz_str)

    def local_date_parser_2_utc(date_str):
        date = datetime.datetime.strptime(date_str, format_str)
        return local_tz.localize(date).astimezone(pytz.utc)
    global date_parser
    date_parser = local_date_parser_2_utc

date_parser = None
set_date_parser("UTC", "%Y.%m.%d-%H:%M")

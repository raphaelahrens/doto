# -*- coding: utf-8 -*-
"""
This module holds a common parser for the add and modify command.
"""
import cli
import pytz
import datetime


def to_unicode(string):
    """
    Turn the given string into a python unicode string.

    This function uses the local encoding and turns the string a unicode string.

    @param string the string that will recoded to unicode.

    """
    return string.decode(cli.util.LOCAL_ENCODING)


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

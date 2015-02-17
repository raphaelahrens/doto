# -*- coding: utf-8 -*-
"""
The command "del" can be used to delete an appointment from the Done!Tools store.

An example of its use would be
    $ doto task del 10

"""
import cli.util

COMMAND = "del"
CONF_DEF = {}


def init_parser(subparsers):
    """ Initialize the subparser. """
    parser = subparsers.add_parser(COMMAND, help="delete a appointment from the list.")
    parser.add_argument("id", type=int, help="the id of the appointment which should be deleted.")


def main(store, args, *_):
    """ Delete the given appointment in args.id. """

    del_apmt, error = cli.cmd.apmt.get_cached_apmt(store, args.id)
    if not del_apmt:
        return error
    store.delete(del_apmt)
    try:
        store.save()
    except:
        cli.util.uprint(("It was not possible to delete the appointment with the id " + cli.util.ID_FORMAT + ":\n\t %r") % (args.id, del_apmt))
        return 4

    cli.util.uprint(("Deleted event with id " + cli.util.ID_FORMAT + ":\n\t Title: %s") % (args.id, del_apmt.event_id, del_apmt.title))
    return 0

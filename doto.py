#!/usr/bin/env python2

"""
The Done!Tools are a collection of tools to handle task and events.


doto add  "Title" "descripton"
doto list
doto

"""

import argparse
import sys
import util
import config
import db
import cli
import cli.ls
import cli.add
import cli.delete


EXIT_CODES = util.enum(unknown_cmd=1)


def main():
    parser = argparse.ArgumentParser(prog='doto', description="The Done!Tools are a collection of tools to handle task and events.", epilog="")
    subparsers = parser.add_subparsers(help='command', dest="cmd")
    cli.add.init_parser(subparsers)
    cli.delete.init_parser(subparsers)
    cli.ls.init_parser(subparsers)
    args = parser.parse_args()
    store = db.DBStore(config.TASK_STORE)
    if args.cmd == "ls":
        cli.ls.list_tasks(store, args)
    elif args.cmd == "add":
        cli.add.add_new_task(store, args)
    elif args.cmd == "add":
        cli.add.add_new_task(store, args)
    else:
        sys.exit(EXIT_CODES.unknown_cmd)
    store

if __name__ == "__main__":
    main()

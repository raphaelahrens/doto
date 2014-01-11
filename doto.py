#!/usr/bin/env python2

"""
The Done!Tools are a collection of tools to handle task and events.


doto add  "Title" "descripton"
doto list
doto

"""

import argparse
import sys
import task


def add_new_task(args, store):
    tsk = task.Task(args.title, args.description)
    print tsk


def init_add_parser(subparsers):
    parser = subparsers.add_parser("add", help="Add a new task to the task list")
    parser.add_argument("title", type=str, help="The title of the new task")
    parser.add_argument("description", type=str, help=" of the new task")
    parser.add_argument("--due", type=task.Date.local_str, help="the estimated completion date.")
    parser.add_argument("--difficulty", type=int, choices=range(0, 4), help="the estimated difficulty of the task.")


def init_del_parser(subparsers):
    parser = subparsers.add_parser('del', help='delete a task from the list.')
    parser.add_argument("id", type=int, help="the id of the task which should be deleted.")


def init_list_parser(subparsers):
    parser = subparsers.add_parser('list', help='list tasks.')
    parser.add_argument("--all", type=int, help="list all tasks.")


def main():
    parser = argparse.ArgumentParser(prog='doto', description="The Done!Tools are a collection of tools to handle task and events.", epilog="")
    subparsers = parser.add_subparsers(help='command', dest="cmd")
    init_add_parser(subparsers)
    init_del_parser(subparsers)
    init_list_parser(subparsers)
    args = parser.parse_args()
    print args
    sys.exit(1)

if __name__ == "__main__":
    main()

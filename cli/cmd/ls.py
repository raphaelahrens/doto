# -*- coding: utf-8 -*-
import cli.util
import config


COMMAND = "ls"


def init_parser(subparsers):
    parser = subparsers.add_parser(COMMAND, help="list tasks.")
    parser.add_argument("--all", action="store_true", help="list all tasks.")


def extract_task_data(tsk):
    return (tsk.task_id,
            tsk.title,
            tsk.difficulty,
            "" if tsk.due is None else tsk.due.local_str(config.DATE_CLI_OUT_STR))


def main(store, args):
    tasks = store.get_tasks()
    headers = [("ID", 4), ("Title", 20), ("Diff", 4), ("Due", 15)]

    cli.util.print_table(headers, [extract_task_data(tsk) for tsk in tasks])

    store.close()

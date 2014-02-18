import itertools
import cli.util


def init_parser(subparsers):
    parser = subparsers.add_parser('ls', help='list tasks.')
    parser.add_argument("--all", action="store_true", help="list all tasks.")


def main(store, args):
    tasks = store.get_tasks()
    headers = [("ID", 4), ("Title", 20), ("Diff", 4), ("Due", 10)]

    cli.util.print_table(headers, [(tsk.task_id, tsk.title, tsk.difficulty, tsk.due) for tsk in tasks])

    store.close()

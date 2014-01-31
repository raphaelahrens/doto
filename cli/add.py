import task


def main(store, args):
    tsk = task.Task(args.title, args.description, due=args.due)
    store.save_new(tsk)


def init_parser(subparsers):
    parser = subparsers.add_parser("add", help="Add a new task to the task list")
    parser.add_argument("title", type=str, help="The title of the new task")
    parser.add_argument("description", type=str, help=" of the new task")
    parser.add_argument("--due", type=task.Date.local_from_str, help="the estimated completion date.")
    parser.add_argument("--difficulty", type=int, choices=task.DIFFICULTY.keys, help="the estimated difficulty of the task.")

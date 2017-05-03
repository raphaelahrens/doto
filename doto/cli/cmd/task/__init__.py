
# -*- coding: utf-8 -*-
"""
The command "task" can be used to add a new task to Done!Tools

An example of its use would be
    $ doto add "Document the Add command" "Add still has no doc strings" --difficulty 1

"""
import functools
import doto.cli.sub_cmds
import doto.cli.parser
import doto.model
import doto.model.task


COMMAND = "task"
CONF_DEF = {}
sub_cmds = {}


init_parser = functools.partial(doto.cli.sub_cmds.init_sub_cmd,
                                command=COMMAND,
                                module_name=__name__,
                                help="The task command")


def main(store, args, config, term):
    """Add a new task with the given args"""
    return sub_cmds[args.sub_cmd].main(store, args, config, term)


def get_cached_task(store, cache_id):
    """
    Get the cached task with the cache_id from the given store.

    @param store the store that stores all tasks
    @param cache_id the id of the cached task
    """
    cache_item, cache_error = doto.model.get_cache_item(store, cache_id, doto.model.task.Task)
    if cache_item is None:
        if not cache_error:
            print("There is no task with the id %d" % cache_id)
            return None, 1

        if doto.model.task.get_count(store) > 0:
            print("I don't know which task you want!\nYou should first run:\n\tdoto ls")
            return None, 3
        print('There are no tasks.\nMaybe you would first like to add a new task with:\n\t doto add "title" "description"')
        return None, 2

    return cache_item, 0


def init_task_flags(parser):
    """
    Set the Flags for creating or modifing a task
    """
    # parser.add_argument("--category", type=to_unicode, help="Set the category of this task.")
    # parser.add_argument("--project", type=to_unicode, help="Set the project of this task.")
    parser.add_argument("--difficulty", type=int, choices=doto.model.task.DIFFICULTY.keys, help="the estimated difficulty of the task.")
    parser.add_argument("--due", type=str, help="the estimated completion date.")
    parser.add_argument("--repeat", type=str, help="number of days in which the task should be repeated.")

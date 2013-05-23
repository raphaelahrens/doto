#! /usr/bin/env python

import taskw
import gui.gtk_window as window
from gui.graph import DependencyGraph


class TaskItem:
    def __init__(self, task_dict):
        if "depends" in task_dict:
            self.depends = task_dict["depends"].split(",")
        else:
            self.depends = []
        self.uuid = task_dict["uuid"]
        self.description = task_dict["description"]
        self.status = task_dict["status"]

    def __str__(self):
        return "uuid: %s\n Name: %s \n(%s)" % (self.uuid, self.description, self.status)

    def __repr__(self):
        return "(%s, %s)" % (self.uuid, self.description)


class LayerItem:
    def __init__(self, task):
        self.task = task
        self.follower = []

    def inc_layer(self, follower):
        self.follower += [follower]

    def layer(self):
        return len(self.follower)

    def __repr__(self):
        return "(%d, %s)" % (self.layer(), self.task)


class TaskStore:
    def __init__(self, tw):
        tw = taskw.TaskWarrior()
        all_tasks = tw.load_tasks()
        self.pending = map(TaskItem, all_tasks["pending"])
        self.completed = map(TaskItem, all_tasks["completed"])
        self.task_index = {}
        for item in self.pending + self.completed:
            self.task_index[item.uuid] = item


def create_data(task_store):
    def update_deps(task):
        for dep in task.depends:
            if dep in data and data[task.uuid].layer() <= data[dep].layer():
                data[dep].inc_layer(data[task.uuid])
                update_deps(data[dep].task)
            else:
                data[dep] = LayerItem(task_store.task_index[dep])

    data = {}
    for task in task_store.pending:
        if task.uuid in data:
            data[task.uuid].task = task
        else:
            data[task.uuid] = LayerItem(task)
        update_deps(task)
    return data


def main():
    store = TaskStore(taskw.TaskWarrior())
    layers = create_data(store)
    layer_zero = []
    for item in layers.iteritems():
        if item[1].layer() == 0:
            layer_zero.append(item[1])

    window.run(DependencyGraph(layer_zero))

if __name__ == "__main__":
    main()

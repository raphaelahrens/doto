#! /usr/bin/env python

import taskw
import pygraphviz as pgv
import gui.gtk_window as window


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


class TaskStore:
    def __init__(self, tw):
        tw = taskw.TaskWarrior()
        all_tasks = tw.load_tasks()
        self.pending = map(TaskItem, all_tasks["pending"])
        self.completed = map(TaskItem, all_tasks["completed"])
        self.index = {}
        for item in self.pending + self.completed:
            self.index[item.uuid] = item


def create_data(task_store):
    def add_node(t):
        A.add_node(t.uuid, label=t.description)
        marked.add(t.uuid)
    marked = set()
    A = pgv.AGraph(directed=True)
    for task in task_store.pending:
        add_node(task)
        for dep in task.depends:
            if dep not in marked:
                add_node(task_store.index[dep])
            A.add_edge(dep, task.uuid)
    return A


def main():
    store = TaskStore(taskw.TaskWarrior())
    graph = create_data(store)
    graph.write("test.dot")

    #window.run()

if __name__ == "__main__":
    main()

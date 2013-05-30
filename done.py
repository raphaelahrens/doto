#! /usr/bin/env python

import argparse
import gui.gtk_window as window
import json
import pygraphviz as pgv
import subprocess
import time
import xdot


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    keys = list(value for value in enums.iterkeys())
    ident = enums.copy()
    revert = dict((value, key) for key, value in enums.iteritems())
    enums['keys'] = keys
    enums['ident'] = ident.get
    enums['revert'] = revert.get
    return type('Enum', (), enums)


STATE = enum("completed", "pending", "deleted")

status_colors = {
    STATE.completed: "darkolivegreen4",
    STATE.pending:   "cornflowerblue",
    STATE.deleted:   "red",
}


class TaskItem:
    def __init__(self, task_dict):
        def get_attr(string, default):
            if str in task_dict:
                return task_dict
            else:
                return default
        if "depends" in task_dict:
            self.depends = task_dict["depends"].split(",")
        else:
            self.depends = []

        self._id = task_dict["id"]
        self.uuid = task_dict["uuid"]
        self.description = task_dict["description"]
        self.status = STATE.ident(task_dict["status"])
        self.urgency = task_dict["urgency"]

        self.start = get_attr("start", None)
        self.end = get_attr("end", None)
        self.recur = get_attr("recur", None)
        self.tags = get_attr("tags", None)
        self.modified = get_attr("modified", None)
        self.project = get_attr("project", None)

        self.data = task_dict

    def __str__(self):
        return "uuid: %s\n Name: %s \n(%s)\n\n %s" % (self.uuid, self.description, self.status, self.data)

    def label(self):
        l = [self.description, '\\n', STATE.revert(self.status)]
        if self.start:
            l += [time.ctime(float(self.start))]
        return ''.join(l)

    def __repr__(self):
        return "(%s, %s)" % (self.uuid, self.description)


class TaskStore:
    def __init__(self):
        output = subprocess.check_output(["task", "export"])
        items = map(TaskItem, json.loads("[" + output + "]"))
        self.index = dict((x.uuid, x) for x in items)
        self.pending = [x for x in items if x.status == STATE.pending]


def create_graph(task_store):
    def add_node(t):
       # label = '<<TABLE><TR><TD>%s</TD></TR><TR><TD><IMG SRC="%s"/></TD><TD><IMG SRC="%s"/></TD></TR></TABLE>>'
        A.add_node(t.uuid, URL=t.uuid, label=t.label(), fillcolor=status_colors[t.status])
        marked.add(t.uuid)
    marked = set()
    A = pgv.AGraph(directed=True, rankdir="LR")
    A.node_attr.update(style="rounded, filled", shape="box", color="black")
    for task in task_store.pending:
        add_node(task)
        for dep in task.depends:
            if task_store.index[dep].status != STATE.deleted:
                if dep not in marked:
                    add_node(task_store.index[dep])
                A.add_edge(dep, task.uuid)
    return A


def dep_graph(store):
    def click(widget, url, event):
        print str(store.index[url])
    graph = create_graph(store)
    widget = xdot.DotWidget()
    widget.connect('clicked', click)
    widget.set_dotcode(graph.string())
    return widget


def main():
    store = TaskStore()
    CMD = enum("graph", "view")
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('cmd', metavar='Command', type=lambda x: getattr(CMD, x),
                        nargs='?', default=CMD.graph,
                        help='the command, which will be executed.')
    args = parser.parse_args()
    print args.cmd

    if args.cmd == CMD.graph:
        widget = dep_graph(store)
    elif args.cmd == CMD.graph:
        widget = None

    window.run(widget)

if __name__ == "__main__":
    main()

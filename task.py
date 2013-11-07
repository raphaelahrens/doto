import json
import datetime
import subprocess


def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    keys = list(value for value in enums.iterkeys())
    ident = enums.copy()
    revert = dict((value, key) for key, value in enums.iteritems())
    enums['keys'] = keys
    enums['ident'] = ident.get
    enums['revert'] = revert.get
    return type('Enum', (), enums)

STATE = enum("pending", "started", "blocked", "paused", "completed", "deleted")


class Task:
    """
    Super class of all tasks
    """
    def __init__(self, title, description, created, due, started,
                 state=STATE.pending):
        """
        """
        self.title = unicode(title)
        self.description = unicode(description)
        self.created = created
        self.due = due
        self.started = started
        self.state = state
        self.source = None
        self.category = None


class TWTask(Task):
    def __init__(self, task_dict):
        def get_attr(string, default):
            if str in task_dict:
                return task_dict
            else:
                return default

        def get_time(s, d):
            return datetime.datetime.strptime(d[s], "%Y%m%dT%H%M%SZ") if s in d else None

        _description = "description"
        Task.__init__(self, task_dict[_description][0:100], task_dict[_description],
                      get_time("entry", task_dict),
                      get_time("due", task_dict),
                      get_time("start", task_dict)
                      )
        if "depends" in task_dict:
            self.depends = task_dict["depends"].split(",")
        else:
            self.depends = []

        self._id = task_dict["id"]
        self.uuid = task_dict["uuid"]
        self.status = STATE.ident(task_dict["status"])
        self.urgency = task_dict["urgency"]

        self.end = get_attr("end", None)
        self.recur = get_attr("recur", None)
        self.tags = get_attr("tags", None)
        self.modified = get_attr("modified", None)
        self.project = get_attr("project", None)

        self.data = task_dict

    def __str__(self):
        return unicode("uuid: %s\n Name: %s \n(%s)\n\n %s" % (self.uuid, self.description, self.status, self.data))

    def __repr__(self):
        return "(%s, %s)" % (self.uuid, self.description)


class TaskwarrioirStore:
    def __init__(self):
        output = subprocess.check_output(["task", "export"])
        items = map(TWTask, json.loads("[" + output + "]"))
        self.index = dict((x.uuid, x) for x in items)
        self.pending = [x for x in items if x.status == STATE.pending]

    def get_tasks(self):
        return self.pending

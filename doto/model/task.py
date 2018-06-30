import copy

import doto.model
import doto.statemachine
import doto.model.crud


CREATE_CMD = """
                CREATE TABLE IF NOT EXISTS
                  tasks (
                    id INTEGER NOT NULL,
                    title VARCHAR NOT NULL,
                    description VARCHAR,
                    created TIMESTAMP NOT NULL,
                    state VARCHAR(1) NOT NULL,
                    difficulty INTEGER NOT NULL,
                    due TIMESTAMP,
                    start TIMESTAMP,
                    end TIMESTAMP,
                    repeat INTEGER,
                    PRIMARY KEY (id),
                    FOREIGN KEY(repeat) REFERENCES repeats(id)
                    CHECK (state IN ('i', 'c', 'p', 's', 'b'))
                );
             """


def create_difficulties(**difficulties):
    """
    Create the difficulty values for the task evaluation.

    @return a enum like type
    """
    keys = []
    names = {}
    for name, d_id in difficulties.items():
        names[name] = d_id
        keys.append(d_id)

    keys.sort()
    names["keys"] = keys
    return type("Difficulty", (), names)


DIFFICULTY = create_difficulties(unknown=0,
                                 simple=1,
                                 easy=2,
                                 medium=3,
                                 hard=4
                                 )


def _add_new_state(states, key, name, cls=doto.statemachine.State):
    """
    Add a new state to the dictionary and return the state.

    @param dir the dictionary to which the state will be added.
    @param key the key for the state
    @param name the name of the state

    @return the new state

    """
    state = cls(key, name)
    states[key] = state
    return state


class StateHolder(object):

    """
    This class is used to manage the state of a Task object.

    The StateHolder class holds the current state of the task and supports
    methods to manipulate the state of the task.

    Supported states are pending, started, completed, blocked, interrupted.

    """

    states = {}
    completed = _add_new_state(states, "c", "completed", doto.statemachine.FinalState)
    pending = _add_new_state(states, "p", "pending")
    started = _add_new_state(states, "s", "started")
    blocked = _add_new_state(states, "b", "blocked")
    interrupted = _add_new_state(states, "i", "interrupted")
    pending.add_neighbor(started, "start")
    started.add_neighbor(completed, "complete")
    started.add_neighbor(blocked, "block")
    started.add_neighbor(interrupted, "interrupt")
    blocked.add_neighbor(started, "unblock")
    interrupted.add_neighbor(started, "restart")

    def __init__(self, state=pending):
        assert state.key in StateHolder.states
        self.state = state

    @property
    def key(self):
        """ Return the key of the state. """
        return self.state.key

    def complete(self):
        """ Set the state to complete if itis not already complete. """
        if self.state is StateHolder.completed:
            return False
        self.state = StateHolder.completed
        return True

    def start(self):
        """ Set the state to started if it is not already started.  """
        if self.state is not StateHolder.pending:
            return False
        self.state = StateHolder.started
        return True

    def reset(self):
        """ Reset the state to pending. """
        self.state = StateHolder.pending
        return True

    def next_state(self, action):
        """Set the next state according to the given action."""
        # TODO: unused in cli maybe in gui
        self.state = self.state.next_state(action)

    def get_actions(self):
        """
        Get all possible action from the current state.

        @return a list of the action for the current state.

        """
        # TODO: unused in cli
        return self.state.get_actions()

    def __eq__(self, obj):
        if isinstance(obj, StateHolder):
            return self.key == obj.key
        return self.state == obj

    def __hash__(self):
        return hash(self.key)

    def __ne__(self, obj):
        return not self.__eq__(obj)

    def __str__(self):
        return self.state.name

    def __repr__(self):
        return "StateHolder(state=%s)" % self.state.name

    @classmethod
    def type_def(cls):
        def state_converter(char):
            return StateHolder(StateHolder.states[char.decode()])

        def state_adapter(state):
            return state.key

        return cls, state_adapter, state_converter


def state_def():
    def state_converter(char):
        return StateHolder(StateHolder.states[char.decode()])

    def state_adapter(state):
        return state.key

    return doto.statemachine.State, state_adapter, state_converter


def final_state_def():
    def state_converter(char):
        return StateHolder(StateHolder.states[char.decode()])

    def state_adapter(state):
        return state.key

    return doto.statemachine.FinalState, state_adapter, state_converter


class Task(doto.model.Event):

    """
    Super class of all tasks.

    Task implements the basic functionality of a task.

    """
    __tablename__ = "tasks"

    def __init__(self, title, description, difficulty=DIFFICULTY.unknown, repeat=None):
        super().__init__(title, description)
        self.difficulty = difficulty
        self.state = StateHolder()
        self.schedule = doto.model.TimeSpan()
        self.due = None
        self.repeat = repeat

    @staticmethod
    def row_to_obj(row, store):
        """
        Create Task from database row
        """
        task = doto.model.unwrap_row(store,
                                     row,
                                     Task,
                                     ('title', 'description', 'difficulty'),
                                     ( 'due', 'created', 'state'),
                                     foreign_keys=(('repeat', doto.model.repeat),)
                                     )
        task.schedule = doto.model.TimeSpan(start=row['start'], end=row['end'])
        return task

    @staticmethod
    def obj_to_row(obj):
        row_dict = doto.model.unwrap_obj(obj, ignore_list=['schedule', 'started'])
        row_dict['start'] = obj.schedule.start
        row_dict['end'] = obj.schedule.end
        row_dict['repeat'] = doto.model.get_id(obj.repeat)
        return row_dict

    @property
    def difficulty(self):
        """ Get the difficulty of the task. """
        return self._difficulty

    @difficulty.setter
    def difficulty(self, obj):
        """ Set the difficulty of the task. """
        if obj not in DIFFICULTY.keys:
            raise ValueError
        self._difficulty = obj

    def done(self):
        """
        Finish the task.

        This method marks the task as completed and also sets the end date
        """
        if not self.state.complete():
            return False
        now = doto.model.now_with_tz()
        if self.schedule.start is None:
            self.schedule.start = now

        self.schedule.end = now

        return True

    def start(self):
        """
        Start the task.

        This method marks the task as started and also sets the start date
        """
        if not self.state.start():
            return False
        self.schedule.start = doto.model.now_with_tz()
        return True

    @property
    def started(self):
        return self.state.state is StateHolder.started

    def reset(self):
        """
        Reset the tasks state.

        Set the state of the task to pending.
        """
        if not self.state.reset():
            return False
        self.schedule = doto.model.TimeSpan()
        return True

    def __key(self):
        return (self.title,
                self.description,
                self.state,
                self.difficulty,
                self.due,
                self.created,
                self.schedule,)

    def __eq__(self, obj):
        return isinstance(obj, Task) and self.__key() == obj.__key()

    def __hash__(self):
        return hash(self.__key())

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return (doto.model.Event.__repr__(self)[:-1] + (",state=%r, difficulty=%r)") %
                (self.state,
                 self.difficulty)
                )


TASK_SELECT = """SELECT id,
                        title,
                        description,
                        created,
                        state as "state [StateHolder]",
                        difficulty,
                        due,
                        start,
                        end,
                        repeat
                 FROM tasks
               """


count_query = 'SELECT COUNT(id) FROM tasks'


def _get_tasks(store, query, args=None):
    return store.query(Task.row_to_obj, query, args)


def get_many(store, limit=10):
    """
    Get a list of all tasks.

    @param cache if True the result will be stored in the cache
            so a cache_id can be used. Default=False
    @param limit Set the maximum number of returned items. Default=10
            If limit is zero there is no limit

    """
    if limit is None:
        return _get_tasks(store, TASK_SELECT + ';')
    else:
        return _get_tasks(store, TASK_SELECT + ' LIMIT ?;', (limit,))


def create_repeat(store, task):
    """ Create a repeated appointment """
    new_task = copy.copy(task)
    new_task.reset()
    now = doto.model.now_with_tz()
    next_dt = now if now > task.due else task.due
    new_task.due = new_task.repeat.next(next_dt)
    new_task.created = now
    # TODO: This cries for a transaction
    add_new(store, new_task)
    new_task.repeat.task = new_task.id
    doto.model.repeat.update(store, new_task.repeat)
    return new_task


def get_open_tasks(store, limit=20):
    """
    Get all task which are not completed.

    @param cache if True the result will be stored in the cache
            so a cache_id can be used. Default=False
    @param limit Set the maximum number of returned items. Default=10

    @return A list of unfinished tasks
    """
    if limit is None:
        return _get_tasks(store,
                          TASK_SELECT + 'WHERE state != ? ;', (StateHolder.completed,))
    else:
        return _get_tasks(store,
                          TASK_SELECT + 'WHERE state != ? LIMIT ?;', (StateHolder.completed, limit,))


insert_query = """INSERT INTO tasks ( title,  description,  created,  state,  difficulty,  due,  start,  end,  repeat)
                             VALUES (:title, :description, :created, :state, :difficulty, :due, :start, :end, :repeat)
                  ;
               """
update_query = """UPDATE tasks SET title = :title,
                                   description = :description,
                                   created = :created,
                                   state = :state,
                                   difficulty = :difficulty,
                                   due = :due,
                                   start = :start,
                                   end = :end,
                                   repeat = :repeat
                         WHERE id = :id;
               """
delete_query = 'DELETE FROM tasks WHERE id = ?;'
select_query = TASK_SELECT + ' WHERE id = :id;'
update = doto.model.crud.update(update_query, Task)
add_new = doto.model.crud.insert(insert_query, Task, add_fn=doto.model.crud.add_and_cache)
delete = doto.model.crud.delete(delete_query)
get = doto.model.crud.get(select_query, Task)
get_count = doto.model.crud.get_count(count_query)


doto.model.setup_module(CREATE_CMD, (StateHolder.type_def(),
                                     state_def(),
                                     final_state_def()))

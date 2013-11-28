class State(object):
    def __init__(self, key, name=None):
        self._key = key
        self._neighbors = {}
        self._name = name

    @property
    def key(self):
        return self._key

    def set_neighbor(self, neighbor, action):
        self._neighbors[action] = neighbor

    def next_state(self, action):
        return self._neighbors[action]

    def get_neighbors(self):
        return self._neighbors.keys()

    def __str__(self):
        return "State: %s" % (self._name)

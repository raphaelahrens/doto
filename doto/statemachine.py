"""
The state module deifnes a small state machine.

In this module are class to create a small State machine nothing fancy.

"""


class AbstractState(object):

    """
    An abstract state.

    This class defines a basic state with a name and a key.

    """

    def __init__(self, key, name):
        self._key = key
        self._name = name

    @property
    def key(self):
        """
        Getter for the key member.

        @return the key

        """
        return self._key

    @property
    def name(self):
        """
        Getter for the name member.

        @return the name

        """
        return self._name

    def __str__(self):
        return "State: %s" % (self._name)

    def add_neighbor(self, neighbor, action):
        """
        Add a new neighbor to that state.

        This methods needs to be implemented by the subclass.

        """
        raise NotImplementedError()

    def next_state(self, action):
        """
        Go to the next state.

        This methods needs to be implemented by the subclass.

        @param action the action which is used to go to the next state

        """
        raise NotImplementedError()

    def get_actions(self):
        """
        Getter for the neighbors.

        This method needs to be implemented by the subclass

        """
        raise NotImplementedError()

    def is_final(self):
        """
        Returns True if this state is a final state.

        @return False since this state is not a final state

        """
        return False


class State(AbstractState):

    """The State class is a simple state for a state machine."""

    def __init__(self, key, name=None):
        AbstractState.__init__(self, key, name)
        self._neighbors = {}

    def add_neighbor(self, neighbor, action):
        """
        Add a neighbor to this state.

        @param neighbor the new neighbor
        @param action the action to get to the new neighbor

        """
        self._neighbors[action] = neighbor

    def next_state(self, action):
        """
        Go to the next neighbor with the following action.

        The action parameter is used to decide which neighbor
        state will be returned by this method.

        @param action the action

        @return the followup state

        """
        return self._neighbors[action]

    def get_actions(self):
        """
        Getter for all possible actions to get from this state to the next.

        @return all possible actions

        """
        return list(self._neighbors.keys())


class FinalState(AbstractState):

    """
    A FinalState object is represents a final state.

    A final state indicates that a state machine has come to a halt.

    """

    def __init__(self, key, name):
        AbstractState.__init__(self, key, name)

    def add_neighbor(self, **arg):
        """
        Add a neighbor to this state.

        This method is not usable since this is final state.

        @throws FinalStateException

        """
        raise FinalStateException("A final state has no neigbors since it is final.")

    def next_state(self, action):
        """
        Go to the next neighbor with the following action.

        This method is not usable since this is final state.

        @throws FinalStateException

        """
        raise FinalStateException("This is a final state. There is no next state.")

    def get_actions(self):
        """
        Getter for all possible actions to get from this state to the next.

        This method is not usable since this is final state.

        @throws FinalStateException

        """
        return []

    def is_final(self):
        """
        Returns True if this is a final state.

        @returns True since this is a final state
        """
        return True


class FinalStateException(Exception):

    """
    The FinalStateException is used by the FinalState.

    The Exception is to indicate that a method was called with a final state.

    """

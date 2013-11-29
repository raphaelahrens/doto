"""
This module holds all classes to serialize a class into a JSON encoded string.

Most important is the interface which a class only needs to support,
so it can be used by the TaskEncoder and TaskDecoder

"""

import json


class JSONSerialize(object):

    """
    This class is an interface for all serializable class.

    A class that wants to be JSON serializable just needs to
    implement all methods of this interface.

    """

    ser_classes = {}

    module_id = "__module__"
    class_id = "__class__"

    @classmethod
    def create_dict(cls, members):
        """
        The method takes a dictionary and adds the class and module information.

        @param members the dictionary with the serializable data
        @return the merged dictionary

        """
        assert(type(members) == dict)
        ret_dict = {JSONSerialize.module_id: cls.__module__,
                    JSONSerialize.class_id: cls.__name__}
        ret_dict.update(members)
        return ret_dict

    @classmethod
    def from_json(cls, d):
        """
        Use the dictionary d and creates a new object of this class.

        @param d the dictionary which was created from a JSON encoded string
        @return the object created from the dictionary

        """
        # Here we create a simple object which we can form into the object we
        # need. tmp could also be of the type object
        tmp = JSONSerialize()
        tmp.__dict__ = d  # pylint: disable=W0201
        tmp.__class__ = cls
        return tmp

    def json_serialize(self):
        """
        The method returns a dictionary which can be serialized into JSON.

        The dictionary returned by the message has the following form:
            {class, module, member1, member2, ...}
        A subclass is free to overwrite this method to create a better
        JSON representation.

        @return the dictionary created

        """
        return self.__class__.create_dict(self.__dict__)


class EncodeError(Exception):

    """This Exception is raised by the TaskEncoder."""

    pass


class TaskEncoder(json.JSONEncoder):

    """TaskEncoder is used to encode JSONSerialize object to JSON."""

    def default(self, obj):  # pylint: disable=E0202
        """
        The given object will be turned in for a dictionary.

        If the object is an instance of JSONSerialize the return value
        will be equal to obj.json_serialize()

        @return the serialized dirctionary

        """
        if isinstance(obj, JSONSerialize):
            return obj.json_serialize()
        return json.JSONEncoder.default(self, obj)


def _check_for_interface(d):
    if JSONSerialize.class_id in d and JSONSerialize.module_id in d:
        module_name = d.pop(JSONSerialize.module_id)
        class_name = d.pop(JSONSerialize.class_id)
        module_o = __import__(module_name)
        class_o = getattr(module_o, class_name)
        return class_o.from_json(d)
    else:
        return d


class TaskDecoder(json.JSONDecoder):

    """TaskDecoder is used to desirialize a Task-JSON string."""

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=_check_for_interface)

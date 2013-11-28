"""
In this module all classes to serialize a class into a JSON encoded string
"""

import json


class JSONSerialize(object):
    """

    """
    ser_classes = {}

    module_id = "__module__"
    class_id = "__class__"

    @classmethod
    def create_dict(cls, members):
        """
        This method takes the dictionary (member) and
        adds the class and module information.

        @param members the dictionary which will be merged with the class and module information
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
        This classmethod takes the dictionary d and creates an object of this class.

        @param d the dictionary which was created from a JSON encoded string
        @return the object created from the dictionary
        """
        # Here we create a simple object which we can form into the object we
        # need. tmp could also be of the type object
        tmp = JSONSerialize()
        tmp.__dict__ = d
        tmp.__class__ = cls
        return tmp

    def json_serialize(self):
        """
        This method returns a dictionary of the form {class, module, member1, member2, ...}

        The method is used to serialize an  of JSONSerialize to a JSON encoded string.

        A subclass is free to overwrite this method to create a better JSON representation.
        """
        return self.__class__.create_dict(self.__dict__)


class EncodeError(Exception):
    """
    This Exception is raised by the TaskEncoder
    """
    pass


class TaskEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, JSONSerialize):
            return o.json_serialize()


class TaskDecoder(json.JSONDecoder):

    def __init__(self):
        json.JSONDecoder.__init__(self, object_hook=self.check_for_interface)

    def check_for_interface(self, d):
        if JSONSerialize.class_id in d and JSONSerialize.module_id in d:
            module_name = d.pop(JSONSerialize.module_id)
            class_name = d.pop(JSONSerialize.class_id)
            module_o = __import__(module_name)
            class_o = getattr(module_o, class_name)
            return class_o.from_json(d)
        else:
            return d

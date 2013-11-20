import json


class JSONSerialize(object):
    ser_classes = {}

    module_id = "__module__"
    class_id = "__class__"

    @classmethod
    def add_class(cls):
        JSONSerialize.ser_classes[cls.__name__] = cls

    @classmethod
    def create_dict(cls, members):
        ret_dict = {JSONSerialize.module_id: cls.__module__,
                    JSONSerialize.class_id: cls.__name__}
        ret_dict.update(members)
        return ret_dict

    @classmethod
    def from_json(cls, d):
        tmp = JSONSerialize()
        tmp.__dict__ = d
        tmp.__class__ = cls
        return tmp

    def json_serialize(self):
        return self.__class__.create_dict(self.__dict__)


class EncodeError(Exception):
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

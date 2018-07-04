'''Done!Tools config file.'''

from typing import Union
import json


class Section(object):
    def __init__(self, values: dict) -> None:
        self.__values = {k: parse_section(v) for k, v in values.items()}

    def __getattr__(self, name: str):
        return self.__values[name]


def parse_section(value: Union[dict, str]) -> Union[Section, str]:
    if isinstance(value, dict):
        return Section(value)
    return value


def merge_confs(defaults: dict, new_values: dict) -> dict:
    for k, v in new_values.items():
        if k in defaults and isinstance(defaults[k], dict) and isinstance(v, dict):
            defaults[k] = merge_confs(defaults[k], v)
        else:
            defaults[k] = v
    return defaults


class Config(object):
    '''
    Config holds and manages a configuration
    '''

    def __init__(self, config_file: str, defaults: dict) -> None:
        try:
            conf_fd = open(config_file)
            config_dict = json.load(conf_fd)
            self.__values = Section(merge_confs(defaults, config_dict))
        except FileNotFoundError:
            self.__values = Section(defaults)

    def __getattr__(self, name: str):
        return getattr(self.__values, name)

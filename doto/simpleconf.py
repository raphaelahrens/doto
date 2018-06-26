# -*- coding: utf-8 -*-
"""Done!Tools config file."""

import sys

import configparser


class Value(object):
    """
    Value holds a configuration value and
    can return parsed version of that value.
    """
    def __init__(self, value, parser_fn=str):
        self.__parser = parser_fn
        self.__value = parser_fn(value)

    @property
    def value(self):
        """Return the value"""
        return self.__value

    @value.setter
    def value(self, obj):
        """
        Set the value and parse if with the parser function.
        """
        self.__value = self.__parser(obj)


class Section(object):
    """
    Section holds a collection of values of a section of the configuration.
    """
    class SectionIterator(object):
        """ SectionIterator is an iterator for the section"""
        def __init__(self, value_dict):
            self.__iterator = iter(value_dict.items())

        def __next__(self):
            """
            Return the next value in the section.
            On ervery call of next() the Iterator returns
                - the name of the value
                - a string representing the value

            @return the name and str(value)

            """
            name, value = next(self.__iterator)
            return name, str(value.value)

        def __iter__(self):
            return self

    def __init__(self, value_dict):
        self.__values = {name: Value(values) for name, values in value_dict.items()}

    def set_value(self, name, obj):
        """ Set the value with name to the given str object. """
        self.__values[name].value = obj

    def __getattr__(self, name):
        return self.__values[name].value

    def __iter__(self):
        return Section.SectionIterator(self.__values)


class Config(object):
    """
    Config holds manages a configuration and stores the config values in a flat hirachie.

    The hirachie of Config looks like  the following:
        Config
          |- Section
          |     |- Value
          |     |- Value
          |- Section
          |     |- Value

    """
    def __init__(self, config_file, defaults):
        self.__sections = {name: Section(values) for name, values in defaults.items()}
        self.parse_config(config_file)

    def parse_config(self, filename):
        """
        Parse the given file and override all values of the current config.

        @param filename the path to the config file.
        """
        parser = configparser.SafeConfigParser()
        parser.read(filename)
        for sec_name in parser.sections():
            section = self.__sections[sec_name]
            for name, value in parser.items(sec_name):
                section.set_value(name, value)

    def __getattr__(self, name):
        return self.__sections[name]

    def print_config(self):
        """
        Write the configuration to standard out.
        """
        parser = configparser.SafeConfigParser()
        for s_name, section in self.__sections.items():
            parser.add_section(s_name)
            for v_name, value in section:
                parser.set(s_name, v_name, value.replace('%', '%%'))
        parser.write(sys.stdout)

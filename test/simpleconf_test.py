"""Unitests for the task module."""

import unittest
import simpleconf


class TestConfig(unittest.TestCase):

    """Unittest for the Config class."""
    defaults = {"abc": {"a": "1", "b": "2", "c": "3"}}

    @classmethod
    def setUpClass(cls):
        """ ."""
        pass

    def test_default_values(self):
        conf = simpleconf.Config("test/configs/notThereRC", TestConfig.defaults)
        self.assertEqual(conf.abc.a, "1")
        self.assertEqual(conf.abc.b, "2")
        self.assertEqual(conf.abc.c, "3")

    def test_load_file(self):
        conf = simpleconf.Config("test/configs/testrc.1", TestConfig.defaults)
        self.assertEqual(conf.abc.a, "1")
        self.assertEqual(conf.abc.b, "2")
        self.assertEqual(conf.abc.c, "4")

    def test_load_2_file(self):
        conf = simpleconf.Config("test/configs/testrc.1", TestConfig.defaults)
        self.assertEqual(conf.abc.a, "1")
        self.assertEqual(conf.abc.b, "2")
        self.assertEqual(conf.abc.c, "4")

        conf.parse_config("test/configs/testrc.2")
        self.assertEqual(conf.abc.b, "5")

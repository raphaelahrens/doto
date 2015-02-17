# -*- coding: utf-8 -*-

import importlib
import pkgutil
import sys


def import_commands(path, name):
    """Import all commands dynamicylly from cli.cmd."""
    commands = {}
    for _, modname, ispkg in pkgutil.iter_modules(path, name + "."):
            module = importlib.import_module(modname)
            commands[module.COMMAND] = module
    return commands


def init_sub_cmd(subparser, command, module_name, help):
    """
    Initialize the enviroment.

    This includes
        - the parser and subpurser,
        - and the enviroment variables.

    @param commands the modules of the cli commands

    """
    parser = subparser.add_parser(command, help=help)
    module = sys.modules[module_name]
    commands = import_commands(module.__path__, module.__name__)
    subparsers = parser.add_subparsers(help="command", dest="sub_cmd")
    for cmd in commands.values():
        cmd.init_parser(subparsers)
    module.sub_cmds = commands

import importlib
import pkgutil
import sys


def import_commands(module):
    """Import all commands dynamicylly from cli.cmd."""
    commands = {}
    path = module.__path__
    name = module.__name__
    for _, modname, _ in pkgutil.iter_modules(path, name + "."):
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
    commands = import_commands(module)
    subparsers = parser.add_subparsers(help="command", dest="sub_cmd")
    for cmd in commands.values():
        cmd.init_parser(subparsers)
    module.sub_cmds.update(commands)


def main(sub_cmds):
    """Add a new task with the given arguments."""

    def exec_cmd(store, args, config, term):
        """ Closure with the subcommand execution"""
        if args.sub_cmd is None:
            pass

        return sub_cmds[args.sub_cmd].main(store, args, config, term)

    return exec_cmd

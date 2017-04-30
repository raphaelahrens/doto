import argparse
import shutil

import doto.cli
import doto.cli.cmd
import doto.cli.sub_cmds
import doto.model
import doto.defaultconfig
import doto.util

EXIT_CODES = doto.util.enum(unknown_cmd=1)


def init_env(commands):
    """
    Initialize the enviroment.

    This includes
        - the parser and subpurser,
        - and the enviroment variables.

    @param commands the modules of the cli commands

    """
    parser = argparse.ArgumentParser(prog="doto", description="The Done!Tools are a collection of tools to handle task and events.")
    subparsers = parser.add_subparsers(help='command', dest="cmd")
    for cmd in commands:
        cmd.init_parser(subparsers)
    return parser, parser.parse_args()


def main():
    """
    The main function.

    It initialises the eviroment,
    parses the command line arguments,
    and executes the gvien command.

    """

    # Init phase
    cmds = doto.cli.sub_cmds.import_commands(doto.cli.cmd.__path__, doto.cli.cmd.__name__)
    config = doto.defaultconfig.read_config()
    parser, args = init_env(cmds.values())
    doto.cli.parser.set_date_parser(config.date.local_tz, config.date.cli_input_str)
    term = shutil.get_terminal_size()
    with doto.model.Store(config.path.store, config.path.cache) as store:
        # execute command
        if args.cmd not in cmds:
            parser.print_help()
            return -1
        exit_code = cmds[args.cmd].main(store, args, config, term)
    return exit_code


# -*- coding: utf-8 -*-
"""
The command "punch" can be used to punch in and out time spans.

This command works like a punch clock.
So you can punch in and put for a task and the start and end time is recorded.

An example of its use would be
    $ doto punch in
      Punched in at 12:14 for Task "Title of task"
    $ doto punch out
      Punched out at 18:46
      You spend 4:32 hours on Task "Title of task"

"""
import functools
import cli.sub_cmds
import cli.parser
import cli.printing


COMMAND = "punch"
CONF_DEF = {}
sub_cmds = {}


init_parser = functools.partial(cli.sub_cmds.init_sub_cmd,
                                command=COMMAND,
                                module_name=__name__,
                                help="The punch command")


def main(store, args, config, term):
    """The Main function of the command gets the subcommand and executes it."""
    date_printer = cli.printing.DatePrinter(config)
    return sub_cmds[args.sub_cmd].main(store, args, config, term, date_printer=date_printer)

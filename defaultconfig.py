# -*- coding: utf-8 -*-

import os.path
import simpleconf

USER_PATH = os.path.join(os.path.expanduser("~"), ".config", "doto")

CONFIG_FILE = os.path.join(USER_PATH, "dotorc")

CONF_DEF = {"path": {"icons": "/home/tant/pomodoro/",
                     "user": USER_PATH,
                     "store": os.path.join(USER_PATH, "store.db"),
                     "cache": os.path.join(USER_PATH, "cache")
                     },
            "date": {"short_out_str": "%d. %b. %Y",
                     "full_out_str": "%d.%m.%Y-%H:%M",
                     "cli_input_str": "%Y.%m.%d-%H:%M",
                     "local_tz": "Europe/Berlin"
                     }
            }


def read_config():
    """
    Read in the config with the default values.

    @return the config object
    """
    return simpleconf.Config(os.getenv("DOTO_CONFIG", CONFIG_FILE), CONF_DEF)

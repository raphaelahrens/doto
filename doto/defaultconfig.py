"""
This module defines the default values for the configuration object
"""
import os.path

import doto.simpleconf

USER_PATH = os.path.join(os.path.expanduser("~"), ".config", "doto")

CONFIG_FILE = os.path.join(USER_PATH, "dotorc")

CONF_DEF = {"path": {"user": USER_PATH,
                     "store": os.path.join(USER_PATH, "store.db"),
                     "cache": os.path.join(USER_PATH, "cache"),
                     "last": os.path.join(USER_PATH, "last"),
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
    return doto.simpleconf.Config(os.getenv("DOTO_CONFIG", CONFIG_FILE), CONF_DEF)

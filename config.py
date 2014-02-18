# -*- coding: utf-8 -*-
"""Done!Tools config file."""

import os.path

TOOLS_PATH = "/home/tant/pomodoro/"

USER_PATH = os.path.expanduser("~") + "/.doto/"

TASK_STORE = USER_PATH + "store.db"

DATE_OUT_STR = "%d. %b. %Y"
DATE_CLI_OUT_STR = "%d.%m.%Y-%H:%M"
DATE_INPUT_STR = "%Y.%m.%d-%H:%M"

LOCAL_TZ = "Europe/Berlin"

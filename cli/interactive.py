
# -*- coding: utf-8 -*-
"""
"""

import cli.util


class DialogAbortError(Exception):
    pass


class DialogBoundError(Exception):
    pass


def dialog(question, anwsers):
    cli.util.uprint(question)
    i = 0
    for anwser in anwsers:
        cli.util.uprint(u"%d) %s" % (i, anwser))
        i += 1
    cli.util.uprint(u"\nq) Abort")
    cli.util.uprint_list
    user_reply = raw_input("?>")

    if user_reply == u"q":
        raise DialogAbortError()
    # throws ValueError
    result = int(user_reply)

    if result >= i:
        raise DialogBoundError("The anwsers %d was bigger than maximum.")
    elif result < 0:
        raise DialogBoundError("The anwsers must be positive.")

    return result

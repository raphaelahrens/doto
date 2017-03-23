"""
"""

import doto.cli.util


class DialogAbortError(Exception):
    pass


class DialogBoundError(Exception):
    pass


def dialog(question, anwsers):
    print(question)
    i = 0
    for anwser in anwsers:
        print("%d) %s" % (i, anwser))
        i += 1
    print("\nq) Abort")
    doto.cli.util.print_list
    user_reply = input("?>")

    if user_reply == "q":
        raise DialogAbortError()
    # throws ValueError
    result = int(user_reply)

    if result >= i:
        raise DialogBoundError("The anwsers %d was bigger than maximum.")
    elif result < 0:
        raise DialogBoundError("The anwsers must be positive.")

    return result

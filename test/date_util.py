#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import datetime
import sys


def main():
    days = int(sys.argv[1])
    hours = int(sys.argv[2])
    minutes = int(sys.argv[3])

    seconds = (hours * 60 + minutes) * 60
    t_plus = datetime.datetime.now() + datetime.timedelta(days, seconds)

    print('{:%Y.%m.%d-%H:%M}'.format(t_plus))

if __name__ == "__main__":
    main()

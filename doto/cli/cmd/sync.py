'''
The command sync synchronizes doto with all configured sources

An example of its use is
    $ doto sync

'''
import datetime
import getpass
import caldav
import pprint

import doto.model.calendar

COMMAND = 'sync'
CONF_DEF = {}

APMT_LIMIT = datetime.timedelta(14, 0, 0)


def init_parser(subparsers):
    '''Initialize the subparser of ls.'''

    subparsers.add_parser(COMMAND, help='synchronize events.')


def main(store, args, config, term):
    '''
    Synchronize doto with other sources

    '''
    user = 'ahrens'
    password = getpass.getpass()
    url = 'https://webmail.fit.fraunhofer.de/SOGo/dav/'
    client = caldav.DAVClient(url, username=user, password=password)

    principal = client.principal()
    calendars = principal.calendars()

    for cal in calendars:
        pprint.pprint(cal)
        pprint.pprint(cal.name)
        pprint.pprint(dir(cal))
        pprint.pprint(vars(cal))

        e = cal.events()[0]
        pprint.pprint(e)
        pprint.pprint(vars(e))

    return 0

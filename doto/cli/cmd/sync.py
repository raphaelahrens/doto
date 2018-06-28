'''
The command sync synchronizes doto with all configured sources

An example of its use is
    $ doto sync

'''
import datetime
import getpass

import caldav


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
    client = caldav.DAVClient(url, username=user, password=password)
    calendar = caldav.Calendar(client, url)

    print(calendar)

    return 0

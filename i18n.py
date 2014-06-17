# -*- coding: utf-8 -*-
"""The module defines erverything that is needed for the gettext transalation."""
import os
import locale
import gettext

# Change this variable to your app name!
#  The translation files will be under
#  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
APP_NAME = "DoneTools"

APP_DIR = "/home/tant/pomodoro/"
LOCALE_DIR = os.path.join(APP_DIR, "i18n")  # .mo files will then be located in APP_Dir/i18n/LANGUAGECODE/LC_MESSAGES/

# Now we need to choose the language. We will provide a list, and gettext
# will use the first translation available in the list
#
#  In maemo it is in the LANG environment variable
#  (on desktop is usually LANGUAGES)
DEFAULT_LANGUAGES = os.environ.get("LANG", "").split(":")
DEFAULT_LANGUAGES += ["en_US"]


def _init_languages():
    """
    Create the gettext languages.

    @return the gettext object

    """

    # Get locals but ignore the encoding (2 arg).
    default_lc, _ = locale.getdefaultlocale()
    if default_lc:
        languages = [default_lc]

    # Concat all languages (env + default locale),
    #  and here we have the languages and location of the translations
    languages += DEFAULT_LANGUAGES
    mo_location = LOCALE_DIR

    # Lets tell those details to gettext
    #  (nothing to change here for you)
    gettext.install(True, localedir=None, unicode=1)

    gettext.find(APP_NAME, mo_location)

    gettext.textdomain(APP_NAME)

    gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")

    return gettext.translation(APP_NAME, mo_location, languages=languages, fallback=True)

LANGUAGE = _init_languages()

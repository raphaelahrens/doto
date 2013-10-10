import os
import gtk

__theme = gtk.icon_theme_get_default()

_path = "/usr/local/share/icons/Tango/scalable/"

start = gtk.STOCK_MEDIA_PLAY
ticking = os.path.realpath("/usr/local/share/icons/Tango/scalable/status/appointment-soon.svg")
coffeebreak = os.path.realpath("/home/tant/pomodoro/icons/coffee_break.svg")
pause = gtk.STOCK_MEDIA_PAUSE

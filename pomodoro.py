#!/usr/bin/python2

import gtk
import pynotify
import os
import sys

icon_path = "/usr/local/share/icons/gnome/48x48"

start_icon = os.path.realpath(icon_path + "/status/appointment-soon.png")
break_icon = os.path.realpath("/home/tant/pomodoro/icons/coffee_break.png")
pause_icon = os.path.realpath(icon_path + "/actions/player_pause.png")
summary = "Pomodoro"


class StatusIcon:
    '''
    Main application for the Pomodoro task watcher
    '''
    def __init__(self):
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_file(start_icon)
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.connect("activate", self.left_click_event)
        self.statusicon.set_tooltip("StatusIcon Example")
        self.__pomodoro = Pomodoro(25,5)

        self.__state = self.start

        gtk.timeout_add(1000, self._timeout_callback)

        self.__menu = NotifyMenu(self)

    def left_click_event(self,icon):
        self.__state()

    def set_tooltip(self):
        self.statusicon.set_tooltip("Pomodoro is %s.\nYou have %d:%02d minutes left.\nRounds finished: %d" % self.__pomodoro.get_info())

    def set_icon(self):
        self.statusicon.set_from_file(self.__pomodoro.icon)

    def set_tooltip_and_icon(self):
        self.set_tooltip()
        self.set_icon()

    def _timeout_callback(self):
        self.set_tooltip()
        if self.__pomodoro.count():
            self.set_icon()
        return True

    def start(self):
        self.__pomodoro.start()
        self.__state = self.pause
        self.set_tooltip_and_icon()
        self.__menu.show_running()
    def pause(self):
        self.__pomodoro.pause()
        self.__state = self.start
        self.statusicon.set_from_file(self.__pomodoro.icon)

    def right_click_event(self, icon, button, t_time):
        self.__menu.popup(None, None, gtk.status_icon_position_menu, button, t_time, icon)

    def done(self):
        self.__menu.show_start()
        #here comes the nect step

class NotifyMenu(gtk.Menu):
    def __init__(self, icon):
        gtk.Menu.__init__(self)

        self.start = gtk.MenuItem("Start")
        self.pause = gtk.MenuItem("Pause")
        self.done = gtk.MenuItem("Done")
        self.quit = gtk.MenuItem("Quit")

        self.start.connect("activate", self.callback, icon.start)
        self.pause.connect("activate", self.callback, icon.pause)
        self.done.connect("activate", self.callback, icon.done)
        self.quit.connect("activate", gtk.main_quit)

        self.append(self.start)
        self.append(self.pause)
        self.append(self.done)
        self.append(self.quit)
        self.show_all()
        self.show_start()

    def show_start(self):
        self.start.show()
        self.pause.hide()
        self.done.hide()

    def show_running(self):
        self.start.hide()
        self.pause.show()
        self.done.show()

    def callback(self, widget, func):
        func()

class Pomodoro:
    startmessage = "Pomodoro started.\n It will last %d minutes."
    restartmessage = "Get back to Work .\n You have  %d minutes."
    endmessage = "Pomodoro ended.\n Take a break!\n You have %d minutes."
    pausemessage = "Pomodoro is paused.\n You have %d minutes left."
    def __init__(self, work_limit, break_limit):
        self.__work_limit = work_limit * 60
        self.__break_limit = break_limit * 60
        self.__limit = self.__work_limit
        self.__paused = True



        self.__round_counter = 0

        self._state = "ready"

        self.end_message = self.end_work

        self._icon = start_icon
        self._message = Pomodoro.startmessage

        self._notifyer = NotifyHandler()

    @property
    def icon(self):
        return self._icon

    @property
    def message(self):
        return self._message

    def start(self):
        start_msg= self.__msg(Pomodoro.startmessage, start_icon)
        start_msg.show()
        self._state = "running"
        self.__paused = False

    def count(self):
        if self.__paused:
           return False
        self.__limit -= 1
        if 0 >= self.__limit:
            self.end()
            return True
        return False

    def __minutes_left(self):
        return self.__limit / 60

    def __seconds_left(self):
        return self.__limit % 60

    def __time_left(self):
        return (self.__minutes_left(), self.__seconds_left())

    def pause(self):
        pause_msg= self.__msg(Pomodoro.pausemessage , pause_icon)
        pause_msg.show()
        self._state = "paused"
        self.__paused = True

    def __restart(self, msg, action=None):
        self.__paused = False
        msg.close()

    def end_break(self):
        self.end_message = self.end_work
        self.__limit = self.__work_limit
        self._state = "running"
        self.__paused = True
        return self.__callback_msg(Pomodoro.restartmessage, start_icon, self.__restart, "ok", "Back to work")

    def end_work(self):
        self.end_message = self.end_break
        self.__round_counter += 1
        if self.__round_counter % 4 == 0:
            self.__limit = self.__break_limit*4
        else:
            self.__limit = self.__break_limit
        self._state = "break"
        self.__paused = True
        return self.__callback_msg(Pomodoro.restartmessage, break_icon, self.__restart, "ok", "Take a Break!")
    def end(self):
        end_msg = self.end_message()
        end_msg.show()

    def get_info(self):
        minutes, seconds = self.__time_left()
        return (self._state, minutes, seconds, self.__round_counter)

    def get_worked_time(self):
        return self.__round_counter * self.__work_limit + self.__time_counter

    def __set_icon_and_message(self, icon, msg):
        self._icon = icon
        self._message = msg

    def __msg(self, msg, icon):
        self.__set_icon_and_message(icon, msg)
        return self._notifyer.get_notify_message(msg%self.__minutes_left(), icon)
    def __callback_msg(self, msg,icon, callback, action , string):
        self.__set_icon_and_message(icon, msg)
        return self._notifyer.get_callback_message(msg%self.__minutes_left(), icon, callback, action, string)

class NotifyHandler:
    def __init__(self):
        self._msgs = {}

    def get_notify_message(self, msg, icon):
        msg = pynotify.Notification(summary, msg, icon)
        msg.connect('closed', self._msg_closed)
        self._msgs[id(msg)] = msg
        return msg

    def get_callback_message(self, msg, icon, callback, action, string):
        msg = self.get_notify_message(msg, icon)
        msg.connect('closed', callback)
        msg.set_urgency(pynotify.URGENCY_CRITICAL)
        msg.add_action(action, string, callback)
        return msg

    def _msg_closed(self, msg):
        del self._msgs[id(msg)]

def main():
    pynotify.init("Pomodoro")
    StatusIcon()
    gtk.main()

if __name__ == "__main__":
    sys.exit(main())

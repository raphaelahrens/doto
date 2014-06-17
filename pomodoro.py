#!/usr/bin/env python2
# -*- coding: utf-8 -*-

"""Pomodoro is a simple pomodoro clock and part of the Done!Tools."""
import gtk
import pynotify
import sys

import gui.icon

ICONS = gui.icon.Theme(128)

SUMMARY = "Pomodoro"


class StatusIcon(object):

    """Main application for the Pomodoro task watcher."""

    def __init__(self):
        self.statusicon = gtk.StatusIcon()
        self.statusicon.set_from_pixbuf(ICONS.start.pixbuf)
        self.statusicon.connect("popup-menu", self.right_click_event)
        self.statusicon.connect("activate", self.left_click_event)
        self.statusicon.set_tooltip("StatusIcon Example")
        self.__pomodoro = Pomodoro(25, 5)
        self.__state = self.start
        gtk.timeout_add(1000, self._timeout_callback)
        self.__menu = NotifyMenu(self)

    def left_click_event(self, _):
        """Reaction to a left clock event."""
        self.__state()

    def set_tooltip(self):
        """Set the tool tip of the pomodoro StatusIcon."""
        self.statusicon.set_tooltip("Pomodoro is %s.\nYou have %d:%02d minutes left.\nRounds finished: %d" % self.__pomodoro.get_info())

    def set_icon(self):
        """Set the icon to the state of the pomodoro member."""
        self.statusicon.set_from_pixbuf(self.__pomodoro.icon.pixbuf)

    def set_tooltip_and_icon(self):
        """Set tooltip and icon of the StatusIcon."""
        self.set_tooltip()
        self.set_icon()

    def _timeout_callback(self):
        """Set the tooltip and icon on a time callback."""
        self.set_tooltip()
        if self.__pomodoro.count():
            self.set_icon()
        return True

    def start(self):
        """Start the pomodoro clock."""
        self.__pomodoro.start()
        self.__state = self.pause
        self.set_tooltip_and_icon()
        self.__menu.show_running()

    def pause(self):
        """Pause the pomoodor clock."""
        self.__pomodoro.pause()
        self.__state = self.start
        self.set_tooltip_and_icon()

    def right_click_event(self, icon, button, t_time):
        """React to a right click event."""
        self.__menu.popup(None, None, gtk.status_icon_position_menu, button, t_time, icon)

    def done(self):
        """Mark the task as done."""
        self.__menu.show_start()
        #here comes the nect step


class NotifyMenu(gtk.Menu):

    """The menu for the pomodoro clock."""

    def __init__(self, icon):
        gtk.Menu.__init__(self)
        self.start = gtk.MenuItem("Start")
        self.pause = gtk.MenuItem("Pause")
        self.done = gtk.MenuItem("Done")
        self.quit = gtk.MenuItem("Quit")
        self.start.connect("activate", NotifyMenu.callback, icon.start)
        self.pause.connect("activate", NotifyMenu.callback, icon.pause)
        self.done.connect("activate", NotifyMenu.callback, icon.done)
        self.quit.connect("activate", gtk.main_quit)
        self.append(self.start)
        self.append(self.pause)
        self.append(self.done)
        self.append(self.quit)
        self.show_all()
        self.show_start()

    def show_start(self):
        """Show we are in the started state."""
        self.start.show()
        self.pause.hide()
        self.done.hide()

    def show_running(self):
        """Show we are in the running state."""
        self.start.hide()
        self.pause.show()
        self.done.show()

    @staticmethod
    def callback(_, func):
        """A wrapper to change the signature."""
        func()


class Pomodoro(object):

    """
    The Pomodoro core class.

    This class stores the logic of the pomodoro clock.
    """

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

        self._icon = ICONS.start
        self._message = Pomodoro.startmessage

        self._notifyer = NotifyHandler()

    @property
    def icon(self):
        """Getter for the icon."""
        return self._icon

    @property
    def message(self):
        """Getter for the message."""
        return self._message

    def start(self):
        """Start the clock."""
        start_msg = self.__msg(Pomodoro.startmessage, ICONS.ticking)
        start_msg.show()
        self._state = "running"
        self.__paused = False

    def count(self):
        """Increment the time counter by one."""
        if self.__paused:
            return False
        self.__limit -= 1
        if 0 >= self.__limit:
            self.end()
            return True
        return False

    def __minutes_left(self):
        """
        Getter for the minutes left on the clock.

        @return the minutes  left

        """
        return self.__limit / 60

    def __seconds_left(self):
        """
        Getter for the seconds left on the clock.

        @return the seconds left  [0,60)

        """
        return self.__limit % 60

    def __time_left(self):
        """
        Getter for the

        @return the minutes and seconds left

        """
        return (self.__minutes_left(), self.__seconds_left())

    def pause(self):
        """Pause the clock."""
        pause_msg = self.__msg(Pomodoro.pausemessage, ICONS.pause)
        pause_msg.show()
        self._state = "paused"
        self.__paused = True

    def __restart(self, msg, _):
        """Restart the clock."""
        self.__paused = False
        msg.close()

    def end_break(self):
        """End the break."""
        self.end_message = self.end_work
        self.__limit = self.__work_limit
        self._state = "running"
        return self.__callback_msg(Pomodoro.restartmessage, ICONS.ticking, self.__restart, "ok", "Back to work")

    def end_work(self):
        """End the work run."""
        self.end_message = self.end_break
        self.__round_counter += 1
        if self.__round_counter % 4 == 0:
            self.__limit = self.__break_limit * 4
        else:
            self.__limit = self.__break_limit
        self._state = "break"
        return self.__callback_msg(Pomodoro.restartmessage, ICONS.coffeebreak, self.__restart, "ok", "Take a Break!")

    def end(self):
        """Display the end message and execute the right end method"""
        self.__paused = True
        end_msg = self.end_message()
        end_msg.show()

    def get_info(self):
        """Getter for the state, minutes and seconds left, and the #counts."""
        minutes, seconds = self.__time_left()
        return (self._state, minutes, seconds, self.__round_counter)

    def __set_icon_and_message(self, icon, msg):
        """Setter for the Icon and the message."""
        self._icon = icon
        self._message = msg

    def __msg(self, msg, icon):
        """Send a notifier message."""
        self.__set_icon_and_message(icon, msg)
        return self._notifyer.notify_message(msg % self.__minutes_left(), icon)

    def __callback_msg(self, msg, icon, callback, action, string):
        """Send a notifier message with a callback function."""
        self.__set_icon_and_message(icon, msg)
        return self._notifyer.notify_message(msg % self.__minutes_left(), icon, callback, action, string)


class NotifyHandler(object):

    """The class manages the notifyd messages and there callbacks."""

    def __init__(self):
        self._msgs = {}

    def notify_message(self, msg, icon, callback=None, action="ok", action_str="Ok"):
        """
        Create a new notification message.

        The method returns a new message object with the message text (msg)
        and the icon.

        If the callback argument is given an ok button is displayed.
        The callback gets called when the button is pressed.

        @param msg the message to print
        @param icon the icon for the message
        @param callback the callback function for the close and action event
        @param action the name of the event for the callback (default:ok)
        @param action_str the text on the button on the notify message

        @return the message object

        """
        msg = pynotify.Notification(SUMMARY, msg, icon.filename)
        #Always set the closed callback so we clean up every message object
        msg.connect('closed', self._msg_closed)

        if callback:
            msg.connect('closed', callback)
            msg.set_urgency(pynotify.URGENCY_CRITICAL)
            msg.add_action(action, action_str, callback)

        self._msgs[id(msg)] = msg

        return msg

    def _msg_closed(self, msg):
        """
        Delete the message.

        The message object needs to be stored until they are closed,
        because of the garbage collector.

        @param msg the message object that was closed

        """
        del self._msgs[id(msg)]


def main():
    """
    The main function for the pomodoro clock.

    It starts the gui of the pomodoro clock and displays the StatusIcon.

    """
    pynotify.init("Pomodoro")
    StatusIcon()
    gtk.main()

if __name__ == "__main__":
    sys.exit(main())

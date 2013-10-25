#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import pango
import time

import task


class TaskInfo(gtk.Window):
    """
    This is a GUI to view the Task of the Done!Tools project.
    """

    def delete_event(self, widget, event, data=None):
        """
        Raction to the delete event.
        """
        return False

    def destroy(self, widget, data=None):
        """
        This method ends the application
        """
        gtk.main_quit()

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.connect("delete_event", self.delete_event)

        self.connect("destroy", self.destroy)

        self.summaryview = SummaryView()

        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        lblSummary = gtk.Label("Summary")
#        lblComments = gtk.Label("Comments")
#        lblFiles = gtk.Label("Files")
        self.notebook.append_page(self.summaryview.getLayout(), lblSummary)

        self.add(self.notebook)
        self.show_all()

    def show_task(self, tasks):
        self.summaryview.show_task(tasks[0])


class SummaryView:
    """
    the summary view of the task
    """

    def __init__(self):
        """
        set the view layout
        """
        self.vbox1 = gtk.VBox()
        self.lblTaskTitle = gtk.Label()
        self.lblTaskTitle.set_alignment(0.0, 0.5)
        self.lblTaskTitle.set_padding(10, 5)
        font = pango.FontDescription()
        font.set_size(14000)
        font.set_weight(pango.WEIGHT_BOLD)
        self.lblTaskTitle.modify_font(font)
        self.vbox1.pack_start(self.lblTaskTitle, expand=False)

        font = pango.FontDescription()
        font.set_weight(pango.WEIGHT_BOLD)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        tvDescription = gtk.TextView()
        tvDescription.set_size_request(600, -1)
        #tvDescription.set_justify(gtk.JUSTIFY_LEFT)
        #tvDescription.set_alignment(0.0, 0.0)
        #tvDescription.set_padding(20, 0)
        tvDescription.set_left_margin(20)
        tvDescription.set_wrap_mode(gtk.WRAP_WORD)
        tvDescription.set_editable(False)
        tvDescription.set_accepts_tab(True)
        tvDescription.set_cursor_visible(False)

        self.tbDescription = tvDescription.get_buffer()

        sw.add(tvDescription)
        self.vbox1.pack_start(sw)

        self.lblOriginator = gtk.Label()
        self.lblOriginator.modify_font(font)
        self.lblOriginator.set_padding(10, 0)

        self.imgOriginator = gtk.Image()
        self.imgOriginator.set_size_request(130, 130)

        self.lblOwner = gtk.Label()
        self.lblOwner.modify_font(font)
        self.lblOwner.set_padding(10, 0)

        self.imgOwner = gtk.Image()
        self.imgOwner.set_size_request(130, 130)

        self.lblCreated = gtk.Label()
        self.lblCreated.modify_font(font)
        self.lblCreated.set_padding(10, 0)

        self.lblStarted = gtk.Label()
        self.lblStarted.modify_font(font)
        self.lblStarted.set_padding(10, 0)

        self.lblDue = gtk.Label()
        self.lblDue.modify_font(font)
        self.lblDue.set_padding(10, 0)

        vboxOriginator = gtk.VBox()
        vboxOriginator.pack_start(self.lblOriginator)
        vboxOriginator.pack_start(self.imgOriginator)

        vboxOwner = gtk.VBox()
        vboxOwner.pack_start(self.lblOwner)
        vboxOwner.pack_start(self.imgOwner)

        hboxUser = gtk.HBox()
        hboxUser.pack_start(vboxOriginator)
        hboxUser.pack_start(vboxOwner)

        self.vbox1.pack_start(hboxUser, expand=False)

        hboxDates = gtk.HBox()
        hboxDates.pack_start(self.lblCreated, fill=False)
        hboxDates.pack_start(self.lblStarted)
        hboxDates.pack_start(self.lblDue)
        self.vbox1.pack_start(hboxDates, expand=False, fill=False)

        self.vbox1.show_all()

    def show_task(self, task):
        self.lblTaskTitle.set_text(task.title)

        self.lblOriginator.set_text("Rapahel")
        self.lblOwner.set_text("Sarah")

        self.imgOriginator.set_from_file("./avatars/Bwoob.jpg")

        self.tbDescription.set_text(task.description)
        self.lblCreated.set_text(time.asctime(task.created))
        if task.due:
            self.lblDue.set_text(time.asctime(task.due))
        else:
            self.lblDue.set_text(time.asctime(time.gmtime()))
        if task.started:
            self.lblStarted.set_text(time.asctime(task.started))
        else:
            self.lblStarted.set_text(time.asctime(time.gmtime()))
#       self.lblOriginator.set_text(task.originator)
#       self.lblOwner.set_text(task.owner)

    def getLayout(self):
        return self.vbox1

def main():
    tw_store = task.TaskwarrioirStore()
    hello = TaskInfo()
    hello.show_task(tw_store.get_tasks())
    gtk.main()

if __name__ == "__main__":
    main()

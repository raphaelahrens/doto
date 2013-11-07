#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk
import pango

import datetime

import task
import config
from icon import Theme
import theme

icons = Theme(32)


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
        self.lblTaskTitle.modify_font(theme.title_font)

        self.lblTaskState = gtk.Label()
        self.lblTaskState.set_alignment(0.9, 0.5)
        self.lblTaskState.modify_font(theme.state_font)

        vboxTitle = gtk.VBox()
        vboxTitle.pack_start(self.lblTaskTitle)
        vboxTitle.pack_start(self.lblTaskState)

        self.imgPriority = gtk.Image()

        hboxHeader = gtk.HBox()

        hboxHeader.pack_start(vboxTitle, expand=False, fill=True, padding=5)
        hboxHeader.pack_end(self.imgPriority, expand=False, padding=5)
        self.vbox1.pack_start(hboxHeader, expand=False, padding=5)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        tvDescription = gtk.TextView()
        tvDescription.set_size_request(400, -1)
        tvDescription.set_left_margin(20)
        tvDescription.set_wrap_mode(gtk.WRAP_WORD)
        tvDescription.set_editable(False)
        tvDescription.set_accepts_tab(True)
        tvDescription.set_cursor_visible(False)

        self.tbDescription = tvDescription.get_buffer()

        sw.add(tvDescription)

        self.lblOriginator = DateLabel()

        self.imgOriginator = gtk.Image()
        self.imgOriginator.set_size_request(80 + 10, 80 + 10)

        self.lblOwner = DateLabel()

        self.imgOwner = gtk.Image()
        self.imgOwner.set_size_request(80 + 10, 80 + 10)

        self.lblCreated = DateLabel()

        self.lblStarted = DateLabel()

        self.lblDue = DateLabel()

        hboxUser = gtk.HBox()
        hboxUser.pack_start(self.imgOriginator)
        hboxUser.pack_start(self.imgOwner)

        vboxAttributes = gtk.VBox()

        def create_date_layout(lbl, title, icon):
            box = gtk.HBox()
            vbox = gtk.VBox()
            img = gtk.Image()
            title = gtk.Label(title)
            title.set_alignment(0.0, 0.5)
            title.modify_font(theme.description_font)

            vbox.pack_start(title)
            vbox.pack_start(lbl)
            img.set_from_pixbuf(icon.pixbuf)
            box.pack_start(img, False, False, 2)
            box.pack_start(vbox)
            return box

        vboxAttributes.pack_start(create_date_layout(self.lblCreated, "created on", icons.created), expand=False, fill=False, padding=10)
        vboxAttributes.pack_start(create_date_layout(self.lblStarted, "started on", icons.done), expand=False, fill=False, padding=10)
        vboxAttributes.pack_start(create_date_layout(self.lblDue, "due to", icons.due), expand=False, fill=False, padding=10)
        vboxAttributes.pack_end(hboxUser, expand=False, padding=20)

        vboxOriginator = gtk.VBox()
        vboxOriginator.pack_start(self.lblOriginator)

        vboxOwner = gtk.VBox()
        vboxOwner.pack_start(self.lblOwner)

        hbox1 = gtk.HBox()
        hbox1.pack_start(sw)
        hbox1.pack_start(vboxAttributes, expand=False)

        self.vbox1.pack_start(hbox1)

        self.vbox1.show_all()

    def show_task(self, t):
        self.lblTaskTitle.set_text(t.title)
        self.lblTaskState.set_text("is " + task.STATE.revert(t.state))

        self.lblOriginator.set_text("Rapahel")
        self.lblOwner.set_text("Sarah")

        self.imgOriginator.set_from_pixbuf(pixbuf_from_file("./avatars/Bwoob.jpg", 80))
        self.imgOwner.set_from_pixbuf(pixbuf_from_file("./avatars/business-man-avatar.svg", 80))
        self.imgPriority.set_from_pixbuf(icons.priority[2].pixbuf)

        self.tbDescription.set_text(t.description)
        self.lblCreated.set_date(t.created)
        if t.due:
            self.lblDue.set_date(t.due)
        else:
            self.lblDue.set_date(datetime.datetime.now())
        if t.started:
            self.lblStarted.set_date(t.started)
        else:
            self.lblStarted.set_date(datetime.datetime.now())
#       self.lblOriginator.set_text(t.originator)
#       self.lblOwner.set_text(t.owner)

    def getLayout(self):
        return self.vbox1


class DateLabel(gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self)
        self.modify_font(theme.date_font)

    def set_date(self, date):
        if date:
            str_tmp = date.strftime(config.date_str)
        else:
            str_tmp = ""
        self.set_text(str_tmp)


def pixbuf_from_file(filename, size):
    pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
    pixbuf = pixbuf.scale_simple(80, 80, gtk.gdk.INTERP_BILINEAR)
    return pixbuf


def main():
    tw_store = task.TaskwarrioirStore()
    hello = TaskInfo()
    hello.show_task(tw_store.get_tasks())
    gtk.main()

if __name__ == "__main__":
    main()

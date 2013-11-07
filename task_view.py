#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk

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

        self.vbMain = gtk.VBox()
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

        self.summaryview = SummaryView()

        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        lblSummary = gtk.Label("Summary")
#        lblComments = gtk.Label("Comments")
#        lblFiles = gtk.Label("Files")
        self.notebook.append_page(self.summaryview.getLayout(), lblSummary)

        self.vbMain.pack_start(hboxHeader, expand=False, padding=5)
        self.vbMain.pack_start(self.notebook)

        self.add(self.vbMain)
        self.show_all()

    def show_header(self, t):
        self.lblTaskTitle.set_text(t.title)
        self.lblTaskState.set_text("is " + task.STATE.revert(t.state))
        self.imgPriority.set_from_pixbuf(icons.priority[2].pixbuf)

    def show_task(self, tasks):
        self.show_header(tasks[6])
        self.summaryview.show_task(tasks[6])


class SummaryView:
    """
    the summary view of the task
    """

    def __init__(self):
        """
        set the view layout
        """
        swDescription = gtk.ScrolledWindow()
        swDescription.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)

        tvDescription = gtk.TextView()
        tvDescription.set_size_request(400, -1)
        #tvDescription.set_left_margin(20)
        tvDescription.set_wrap_mode(gtk.WRAP_WORD)
        tvDescription.set_editable(False)
        tvDescription.set_accepts_tab(True)
        tvDescription.set_cursor_visible(False)

        self.tbDescription = tvDescription.get_buffer()

        swDescription.add(tvDescription)

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
            box.pack_start(img, False, False, padding=5)
            box.pack_start(vbox, padding=5)
            return box

        vboxDates = gtk.VBox()
        vboxDates.pack_start(create_date_layout(self.lblCreated, "created on", icons.created), expand=False, fill=False, padding=10)
        vboxDates.pack_start(create_date_layout(self.lblStarted, "started on", icons.done), expand=False, fill=False, padding=10)
        vboxDates.pack_start(create_date_layout(self.lblDue, "due to", icons.due), expand=False, fill=False, padding=10)

        frDates = gtk.Frame()
        frDates.add(vboxDates)
        lbl = gtk.Label("Dates")
        lbl.modify_font(theme.frame_font)
        frDates.set_label_widget(lbl)

        vboxAttributes.pack_start(frDates, expand=False, padding=10)
        vboxAttributes.pack_end(hboxUser, expand=False, padding=20)

        self.hbView = gtk.HBox()
        self.hbView.pack_start(swDescription)
        self.hbView.pack_start(vboxAttributes, expand=False)

        self.hbView.show_all()

    def show_task(self, t):
        self.lblOriginator.set_text("Rapahel")
        self.lblOwner.set_text("Sarah")

        self.imgOriginator.set_from_pixbuf(pixbuf_from_file("./avatars/Bwoob.jpg", 80))
        self.imgOwner.set_from_pixbuf(pixbuf_from_file("./avatars/business-man-avatar.svg", 80))

        self.tbDescription.set_text((t.description + " ") * 100)
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
        return self.hbView


class DateLabel(gtk.Label):
    def __init__(self):
        gtk.Label.__init__(self)
        self.modify_font(theme.date_font)
        self.set_alignment(0.0, 0.5)

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

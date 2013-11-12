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

        self.vboxMain = gtk.VBox()
        self.lblTaskTitle = gtk.Label()
        self.lblTaskTitle.set_alignment(0.0, 0.5)
        self.lblTaskTitle.modify_font(theme.title_font)

        self.lblTaskState = gtk.Label()
        self.lblTaskState.set_alignment(0.9, 0.5)
        self.lblTaskState.modify_font(theme.state_font)

        self.lblDue = DateLabel()
        boxDue = create_date_layout(self.lblDue, "due to", icons.due)
        boxDue.set_size_request(180, -1)

        vboxTitle = gtk.VBox()
        vboxTitle.pack_start(self.lblTaskTitle)
        vboxTitle.pack_start(self.lblTaskState)

        self.imgPriority = gtk.Image()

        hboxHeader = gtk.HBox()

        hboxHeader.pack_start(vboxTitle, expand=False, fill=True, padding=5)
        hboxHeader.pack_end(boxDue, expand=False, fill=False, padding=0)
#        hboxHeader.pack_end(self.imgPriority, expand=False, padding=5)

        self.summaryview = SummaryView()

        self.notebook = gtk.Notebook()
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        lblSummary = gtk.Label("Summary")
        self.notebook.append_page(self.summaryview.getLayout(), lblSummary)
        lblComments = gtk.Label("Comments")
        self.notebook.append_page(gtk.Label("LOL"), lblComments)
        lblFiles = gtk.Label("Files")
        self.notebook.append_page(gtk.Label("LOL"), lblFiles)

        self.vboxMain.pack_start(hboxHeader, expand=False, padding=5)
        self.vboxMain.pack_start(self.notebook)

        self.add(self.vboxMain)
        self.show_all()

    def show_header(self, t):
        self.lblTaskTitle.set_text(t.title)
        self.lblTaskState.set_text("is " + task.STATE.revert(t.state))
        self.imgPriority.set_from_pixbuf(icons.priority[2].pixbuf)
        if t.due:
            self.lblDue.set_time_left(t.due)
        else:
            self.lblDue.set_time_left(datetime.datetime.now())

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
        tvDescription.set_wrap_mode(gtk.WRAP_WORD)
        tvDescription.set_editable(False)
        tvDescription.set_accepts_tab(True)
        tvDescription.set_cursor_visible(False)

        self.tbDescription = tvDescription.get_buffer()

        swDescription.add(tvDescription)

        self.imgOriginator = gtk.Image()
        self.imgOriginator.set_size_request(80 + 10, 80 + 10)

        self.imgOwner = gtk.Image()
        self.imgOwner.set_size_request(80 + 10, 80 + 10)

        self.lblCreated = DateLabel()

        self.lblStarted = DateLabel()

        hboxUser = gtk.HBox()
        hboxUser.pack_start(self.imgOriginator)
        hboxUser.pack_start(self.imgOwner)

        vboxDates = gtk.VBox()
        vboxDates.pack_start(create_date_layout(self.lblCreated, "created on", icons.created), expand=False, fill=False, padding=10)
        vboxDates.pack_start(create_date_layout(self.lblStarted, "started on", icons.done), expand=False, fill=False, padding=10)

        def create_frame(name, widget):
            """
            Create a frame with the name as a label

            @param name The title of the frame
            @param widget The widget inside the frame
            """
            frame = gtk.Frame()
            frame.add(widget)
            lbl = gtk.Label(name)
            lbl.modify_font(theme.frame_font)
            frame.set_label_widget(lbl)
            return frame

        frDates = create_frame("Dates", vboxDates)
        frUser = create_frame("Originator & Owner", hboxUser)

        vboxAttributes = gtk.VBox()
        vboxAttributes.pack_start(frDates, expand=False, padding=10)
        vboxAttributes.pack_end(frUser, expand=False, padding=20)

        self.hboxView = gtk.HBox()
        self.hboxView.pack_start(swDescription)
        self.hboxView.pack_start(vboxAttributes, expand=False)

        self.hboxView.show_all()

    def show_task(self, t):
        """
        Show the view of the task t

        @param t The task
        """
        self.imgOriginator.set_from_pixbuf(pixbuf_from_file("./avatars/Bwoob.jpg", 80))
        self.imgOwner.set_from_pixbuf(pixbuf_from_file("./avatars/business-man-avatar.svg", 80))

        self.tbDescription.set_text((t.description))
        self.lblCreated.set_date(t.created)
        if t.started:
            self.lblStarted.set_date(t.started)
        else:
            self.lblStarted.set_date(datetime.datetime.now())

    def getLayout(self):
        """
        Return the container of this view, so the main window can
        """
        return self.hboxView


class DateLabel(gtk.Label):
    """
    A special label for dates
    """
    def __init__(self):
        gtk.Label.__init__(self)
        self.modify_font(theme.date_font)
        self.set_alignment(0.0, 0.5)

    def set_time_left(self, date):
        """
        Set the label to the time left until today

        @param date The date to display
        """
        t_diff = date - date.today()

        def one_or_more(t, single_str, multiple_str):
            if t == 1:
                self.set_text(single_str % t)
            else:
                self.set_text(multiple_str % t)

        if t_diff.days > 7:
            self.set_text(date.strftime(config.date_str))
        elif t_diff.days > 0:
            one_or_more(t_diff.days, "in %d day", "in %d days")
        elif t_diff.seconds > 3600:
            one_or_more(t_diff.seconds // 3600, "in %d hour", "in %d hours")
        elif t_diff.seconds > 60:
            one_or_more(t_diff.seconds // 60, "in %d minute", "in %d minutes")
        else:
            one_or_more(t_diff.seconds, "in %d second", "in %d seconds")

    def set_date(self, date):
        """
        Display the date in the label

        @param self the Label
        @param date The date to which the label shall be set
        """
        if date:
            str_tmp = date.strftime(config.date_str)
        else:
            str_tmp = ""
        self.set_text(str_tmp)


def create_date_layout(lbl, title, icon):
    #TODO: maybe this is a function of the DateLabel class
    """
    Create a box container with two labels and an icon.

    @param lbl A widget to be put into the box container
    @param title the title for that widget
    @param icon The Icon for the widget
    """
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

"""
This tool is used to display a task.

It displays a single task and all its properties
in one small window.

"""

import pygtk
pygtk.require('2.0')
import gtk
import datetime

import i18n
_ = i18n.LANGUAGE.ugettext

import task
import config
import theme
from icon import Theme

ICONS = Theme(32)


class TaskInfo(gtk.Window):

    """This is a GUI to view the Task of the Done!Tools project."""

    @staticmethod
    def delete_event(widget, event, data=None):  # pylint: disable=W0613
        """
        React to an delete event.

        @return False

        """
        return False

    @staticmethod
    def destroy(widget, data=None):  # pylint: disable=W0613
        """Quit the application."""
        gtk.main_quit()

    def __init__(self):
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)

        self.connect("delete_event", TaskInfo.delete_event)

        self.connect("destroy", TaskInfo.destroy)

        self.vbox_main = gtk.VBox()
        self.lbl_task_title = gtk.Label()
        self.lbl_task_title.set_alignment(0.0, 0.5)
        self.lbl_task_title.modify_font(theme.TITLE_FONT)

        self.lbl_task_state = gtk.Label()
        self.lbl_task_state.set_alignment(0.9, 0.5)
        self.lbl_task_state.modify_font(theme.STATE_FONT)

        self.lbl_due = DateLabel()
        box_due = create_date_layout(self.lbl_due, _("due"), ICONS.due)
        box_due.set_size_request(190, -1)

        vbox_title = gtk.VBox()
        vbox_title.pack_start(self.lbl_task_title)
        vbox_title.pack_start(self.lbl_task_state)

        self.img_priority = gtk.Image()

        hbox_header = gtk.HBox()

        hbox_header.pack_start(vbox_title, expand=False, fill=True, padding=5)
        hbox_header.pack_end(box_due, expand=False, fill=False, padding=0)
#        hboxHeader.pack_end(self.imgPriority, expand=False, padding=5)

        self.summaryview = SummaryView()

        self.notebook = gtk.Notebook()
        self.notebook.set_border_width(4)
        self.notebook.set_tab_pos(gtk.POS_BOTTOM)
        lbl_summary = gtk.Label(_("Summary"))
        self.notebook.append_page(self.summaryview.get_layout(), lbl_summary)
        lbl_comments = gtk.Label(_("Comments"))
        self.notebook.append_page(gtk.Label("LOL"), lbl_comments)
        lbl_files = gtk.Label(_("Files"))
        self.notebook.append_page(gtk.Label("LOL"), lbl_files)

        self.vbox_main.pack_start(hbox_header, expand=False, padding=5)
        self.vbox_main.pack_start(self.notebook)

        self.add(self.vbox_main)
        self.show_all()

    def show_header(self, tsk):
        """
        Display the header of the task.

        @param tsk the task to display

        """
        self.lbl_task_title.set_text(tsk.title)
        self.lbl_task_state.set_text(_("is ") + "pending")  # task.STATE.revert(tsk.state))
        self.img_priority.set_from_pixbuf(ICONS.priority[2].pixbuf)
        if tsk.due:
            self.lbl_due.set_time_left(tsk.due)
        else:
            self.lbl_due.set_time_left(datetime.datetime.now())

    def show_task(self, tsk):
        """
        Display the tsk in a view window.

        @param tsk the task

        """
        self.show_header(tsk)
        self.summaryview.show_task(tsk)


class SummaryView(object):

    """The summary view of the task."""

    def __init__(self):
        sw_description = gtk.ScrolledWindow()
        sw_description.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        sw_description.set_border_width(5)

        tv_description = gtk.TextView()
        tv_description.set_size_request(400, -1)
        tv_description.set_wrap_mode(gtk.WRAP_WORD)
        tv_description.set_editable(False)
        tv_description.set_accepts_tab(True)
        tv_description.set_cursor_visible(False)

        self.tb_description = tv_description.get_buffer()

        sw_description.add(tv_description)

        self.img_originator = gtk.Image()
        self.img_originator.set_size_request(80 + 10, 80 + 10)

        self.img_owner = gtk.Image()
        self.img_owner.set_size_request(80 + 10, 80 + 10)

        self.lbl_created = DateLabel()

        self.lbl_started = DateLabel()

        hbox_user = gtk.HBox()
        hbox_user.pack_start(self.img_originator)
        hbox_user.pack_start(self.img_owner)

        vbox_dates = gtk.VBox()
        vbox_dates.pack_start(create_date_layout(self.lbl_created, _("created on"), ICONS.created), expand=False, fill=False, padding=10)
        vbox_dates.pack_start(create_date_layout(self.lbl_started, _("started on"), ICONS.done), expand=False, fill=False, padding=10)

        def create_frame(name, widget):
            """
            Create a frame with the name as a label

            @param name The title of the frame
            @param widget The widget inside the frame

            """
            frame = gtk.Frame()
            frame.add(widget)
            lbl = gtk.Label(name)
            lbl.modify_font(theme.FRAME_FONT)
            frame.set_label_widget(lbl)
            return frame

        fr_dates = create_frame(_("Dates"), vbox_dates)
        fr_user = create_frame(_("Originator & Owner"), hbox_user)

        vbox_attributes = gtk.VBox()
        vbox_attributes.pack_start(fr_dates, expand=False, padding=5)
        vbox_attributes.pack_end(fr_user, expand=False, padding=5)

        self.hbox_view = gtk.HBox()
        self.hbox_view.pack_start(sw_description, padding=5)
        self.hbox_view.pack_start(vbox_attributes, expand=False, padding=5)

        self.hbox_view.show_all()

    def show_task(self, tsk):
        """
        Show the view of the task tsk.

        @param tsk the task

        """
        self.img_originator.set_from_pixbuf(pixbuf_from_file("./avatars/Bwoob.jpg", 80))
        self.img_owner.set_from_pixbuf(pixbuf_from_file("./avatars/business-man-avatar.svg", 80))

        self.tb_description.set_text((tsk.description))
        self.lbl_created.set_date(tsk.created)
        if tsk.started:
            self.lbl_started.set_date(tsk.started)
        else:
            self.lbl_started.set_date(datetime.datetime.now())

    def get_layout(self):
        """
        Return the container of this view.

        @return the layout of this view

        """
        return self.hbox_view


class DateLabel(gtk.Label):

    """A special label for dates."""

    def __init__(self):
        gtk.Label.__init__(self)
        self.modify_font(theme.DATE_FONT)
        self.set_alignment(0.0, 0.5)

    def set_time_left(self, date):
        """
        Set the label to the time left until now.

        @param date The date to display

        """
        t_span = date - date.now()
        if t_span.days < 0:
            self.set_text(_("over due"))
            return
        if t_span.days < 7:
            self.set_text(_("in ") + task.str_from_time_span(t_span))
            return
        self.set_text(_("to ") + date.strftime(config.DATE_STR))
        return

    def set_date(self, date):
        """
        Display the date in the label.

        @param self the Label
        @param date The date to which the label shall be set

        """
        self.set_text(date.local_str() if date else "")


def create_date_layout(lbl, title, icon):
    # TODO: maybe this is a function of the DateLabel class
    """
    Create a box container with two labels and an icon.

    @param lbl A widget to be put into the box container
    @param title the title for that widget
    @param icon The Icon for the widget

    @return the new box container

    """
    box = gtk.HBox()
    vbox = gtk.VBox()
    img = gtk.Image()
    title = gtk.Label(title)
    title.set_alignment(0.0, 0.5)
    title.modify_font(theme.DESCRIPTION_FONT)

    vbox.pack_start(title)
    vbox.pack_start(lbl)
    img.set_from_pixbuf(icon.pixbuf)
    box.pack_start(img, False, False, padding=5)
    box.pack_start(vbox, padding=5)
    return box


def pixbuf_from_file(filename, size):
    """
    Create a Pixbuf from a filename.

    @param filename the name of the file
    @param size the size of the to be returned Pixbuffer

    @return the newly created Pixbuffer

    """
    pixbuf = gtk.gdk.pixbuf_new_from_file(filename)
    pixbuf = pixbuf.scale_simple(size, size, gtk.gdk.INTERP_BILINEAR)
    return pixbuf


def main():
    """The main function."""
    tw_store = task.TaskwarrioirStore()
    hello = TaskInfo()
    hello.show_task(tw_store.get_tasks()[6])
    gtk.main()

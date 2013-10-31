#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk

import task
from icon import Theme

icons = Theme(24)


class TaskList(gtk.Window):
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

        ## the ListStore stores the Icon, the title, the date of creation, the state, source
        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, gtk.gdk.Pixbuf, str, str, str)

        # create the TreeView using liststore
        treeview = gtk.TreeView(self.liststore)

        # create the TreeViewColumns to display the data
        tvc_title = gtk.TreeViewColumn("Title")
        tvc_created = gtk.TreeViewColumn("Created")

        # add a row with text and a stock item - color strings for
        # the background
        for i in xrange(1, 10):
            self.liststore.append([icons.ticking.pixbuf, icons.priority[0].pixbuf, icons.coffeebreak.pixbuf, 'Open', gtk.STOCK_OPEN, 'Open a File'])
            self.liststore.append([icons.coffeebreak.pixbuf, icons.priority[3].pixbuf, icons.ticking.pixbuf, 'Open', gtk.STOCK_OPEN, 'Open a File'])
            self.liststore.append([icons.pause.pixbuf, icons.priority[2].pixbuf, icons.ticking.pixbuf, 'New', gtk.STOCK_NEW, 'New File'])
            self.liststore.append([icons.coffeebreak.pixbuf, icons.priority[1].pixbuf, icons.pause.pixbuf, 'Print', gtk.STOCK_PRINT, 'Print File'])

        # add columns to treeview
        treeview.append_column(tvc_title)
        treeview.append_column(tvc_created)

        # create a CellRenderers to render the data
        cpb_source = gtk.CellRendererPixbuf()
        cpb_priori = gtk.CellRendererPixbuf()
        cpb_state = gtk.CellRendererPixbuf()
        ct_title = gtk.CellRendererText()
        ct_created = gtk.CellRendererText()

        # set background color property
        #cellpb.set_property('cell-background', 'yellow')
        #cell.set_property('cell-background', 'cyan')
        #cell1.set_property('cell-background', 'red')

        # add the cells to the columns - 2 in the first
        tvc_title.pack_start(cpb_source, False)
        tvc_title.pack_start(cpb_priori, False)
        tvc_title.pack_start(cpb_state, False)
        tvc_title.pack_start(ct_title, True)
        tvc_created.pack_start(ct_created, True)

        # set the cell attributes to the appropriate liststore column
        # GTK+ 2.0 doesn't support the "stock_id" property
        tvc_title.set_attributes(ct_title, text=3)
        tvc_title.set_attributes(cpb_source, pixbuf=0)
        tvc_title.set_attributes(cpb_priori, pixbuf=1)
        tvc_title.set_attributes(cpb_state, pixbuf=2)
        tvc_created.set_attributes(ct_created, text=5)

        # make treeview searchable
        treeview.set_search_column(0)

        # Allow sorting on the column
        tvc_title.set_sort_column_id(-1)

        # Allow drag and drop reordering of rows
        treeview.set_reorderable(True)

        scrolled_window = gtk.ScrolledWindow()
        scrolled_window.set_policy(hscrollbar_policy=gtk.POLICY_NEVER, vscrollbar_policy=gtk.POLICY_AUTOMATIC)

        scrolled_window.add_with_viewport(treeview)

        self.add(scrolled_window)

        self.show_all()

    def show_tasks(self, tasks):
        pass


def main():
    tw_store = task.TaskwarrioirStore()
    hello = TaskList()
    gtk.main()

if __name__ == "__main__":
    main()

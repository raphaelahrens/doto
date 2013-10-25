#!/usr/bin/env python

# example helloworld.py

import pygtk
pygtk.require('2.0')
import gtk

import task
import icon


class TaskView(gtk.Window):
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

        self.liststore = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str, str)

        # create the TreeView using liststore
        treeview = gtk.TreeView(self.liststore)

        # create the TreeViewColumns to display the data
        tvc_title = gtk.TreeViewColumn("Title")
        tvc_created = gtk.TreeViewColumn("Created")

        # add a row with text and a stock item - color strings for
        # the background
        for i in xrange(1,10):
            self.liststore.append([icon.coffeebreak.pixbuf, 'Open', gtk.STOCK_OPEN, 'Open a File', "red"])
            self.liststore.append([icon.pause.pixbuf, 'New', gtk.STOCK_NEW, 'New File', "blue"])
            self.liststore.append([icon.ticking.pixbuf, 'Print', gtk.STOCK_PRINT, 'Print File', "grey"])

        # add columns to treeview
        treeview.append_column(tvc_title)
        treeview.append_column(tvc_created)

        # create a CellRenderers to render the data
        cellpb = gtk.CellRendererPixbuf()
        cell = gtk.CellRendererText()
        cell1 = gtk.CellRendererText()

        # set background color property
        #cellpb.set_property('cell-background', 'yellow')
        #cell.set_property('cell-background', 'cyan')
        #cell1.set_property('cell-background', 'red')

        # add the cells to the columns - 2 in the first
        tvc_title.pack_start(cellpb, False)
        tvc_title.pack_start(cell, True)
        tvc_created.pack_start(cell1, True)

        # set the cell attributes to the appropriate liststore column
        # GTK+ 2.0 doesn't support the "stock_id" property
        tvc_title.set_attributes(cell, text=1)
        tvc_title.set_attributes(cellpb, pixbuf=0)
        tvc_created.set_attributes(cell1, text=3, cell_background=4)

        # make treeview searchable
        treeview.set_search_column(0)

        # Allow sorting on the column
        tvc_title.set_sort_column_id(-1)

        # Allow drag and drop reordering of rows
        treeview.set_reorderable(True)

        self.add(treeview)

        self.show_all()

    def show_tasks(self, tasks):
        pass


def main():
    tw_store = task.TaskwarrioirStore()
    hello = TaskView()
    gtk.main()

if __name__ == "__main__":
    main()

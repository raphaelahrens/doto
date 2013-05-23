#! /usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk


# Create a GTK+ widget on which we will draw using Cairo
class Screen(gtk.DrawingArea):

    # Draw in response to an expose-event
    __gsignals__ = {"expose-event": "override"}

    # Handle the expose-event by drawing
    def do_expose_event(self, event):

        # Create the cairo context

        self.cr = self.window.cairo_create()
        # Restrict Cairo to the exposed area; avoid extra work
        self.cr.rectangle(event.area.x, event.area.y, event.area.width, event.area.height)
        self.cr.clip()

        self.draw(*self.window.get_size())

    def draw(self, width, height):
        pass


# GTK mumbo-jumbo to show the widget in a window and quit when it's closed
def run(widget):
    window = gtk.Window()
    window.set_position(gtk.WIN_POS_CENTER)
    window.set_size_request(1024, 600)
    window.connect("delete-event", gtk.main_quit)
    window.add(widget)
    widget.show()
    window.present()
    gtk.main()

if __name__ == "__main__":
    run(Screen())

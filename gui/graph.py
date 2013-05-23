#! /usr/bin/env python
import gtk_window as window
import cairo


min_width = 2

text_color = cairo.SolidPattern(0, 0, 0)
background_color = {"completed": cairo.SolidPattern(0.1, 0.9, 0),
                    "pending":   cairo.SolidPattern(1, 1.0, 0)
                    }


class DependencyGraph(window.Screen):

    def __init__(self, layers):
        window.Screen.__init__(self)
        self.layer_list = layers
        self.nodes = {}

    def draw(self, width, height):
        self.cr.save()
        # set up a transform so that (0,0) to (1,1)
        # maps to (20, 20) to (width - 40, height - 40)
        self.cr.translate(10, 10)
        self.cr.scale(50, 50)
        for layer in self.layer_list:
            self.draw_task(layer.task)
            self.cr.translate(0, 1.)
        self.cr.restore()

    def draw_task(self, task):
        def draw_text(text, width):
            self.cr.set_source(text_color)
            self.cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            self.cr.set_font_size(0.2)
            self.cr.move_to(width, 0.5)
            self.cr.show_text(text)

        def draw_background():
            bg_h = 1
            x, y, width, heigth, x_a, y_a = self.cr.text_extents(task.description)
            if width < min_width:
                bg_w = min_width
            else:
                bg_w = width + 0.1

            self.cr.rectangle(0, 0, bg_w, bg_h)
            self.cr.set_source(background_color[task.status])
            self.cr.set_line_width(0.03)
            self.cr.set_line_join(cairo.LINE_JOIN_ROUND)
            self.cr.fill_preserve()
            self.cr.set_source(text_color)
            self.cr.stroke()
            draw_text(task.description, (bg_w - width) / 2)
            return self.cr.user_to_device(0, 0)

        self.cr.save()
        self.cr.select_font_face("Courier", cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
        self.cr.set_font_size(0.2)
        self.cr.translate(0.05, 0.05)
        self.cr.scale(.9, .9)
        r = draw_background()
        self.cr.restore()
        return r

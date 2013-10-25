import gtk

_theme = gtk.icon_theme_get_default()


class Icon:
    """
    Icon class which stores the Pixbuf and the file name
    """
    def __init__(self, filename, pixbuf):
        """
        The Constructor for the Icon class

        @param filename the full path to the file of the icon.
        @param pixbuf the Pixbuf object that
        """
        self.__filename = filename
        self.__pixbuf = pixbuf

    @staticmethod
    def new_icon_from_file(filename, size):
        """
        Constructs an Icon object from a file
         The volume of the Icon ist size*size

        @param filename The full path to the file of the icon
        @param The size of the Icon.
        """
        return Icon(filename, gtk.gdk.pixbuf_new_from_file_at_size(filename, size, size))

    @staticmethod
    def new_icon_from_icon_names(icon_names, size):
        """
        Constructs an Icon object from a list of GTK icon names

        @param icon_names A List of names for the icon
        """
        icon_info = _theme.choose_icon(icon_names, size, 0)
        return Icon(icon_info.get_filename(), icon_info.load_icon())

    @property
    def filename(self):
        """
        The method returns the filename of the Icon
        """
        return self.__filename

    @property
    def pixbuf(self):
        """
        The method returns the Pixbuf of the Icon

        @return the Pixbuf object associated with the Icon
        """
        return self.__pixbuf


class Theme:
    """
    The theme class for the Done!Tools
    """
    def __init__(self, size):
        """

        """
        self.start = Icon.new_icon_from_icon_names([gtk.STOCK_MEDIA_PLAY, "player_play"], size)
        self.ticking = Icon.new_icon_from_icon_names(["appointment-soon"], size)
        self.coffeebreak = Icon.new_icon_from_file("/home/tant/pomodoro/icons/coffee_break.svg", size)
        self.pause = Icon.new_icon_from_icon_names([gtk.STOCK_MEDIA_PAUSE, "player_pause"], size)

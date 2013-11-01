import gtk

import config

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

    @param size The size of the Icons for the theme
    """
    def __init__(self, size):
        """

        """
        self._size = size
        self.__start = None
        self.__ticking = None
        self.__coffeebreak = None
        self.__pause = None

        self.__priority = None

    @property
    def start(self):
        if not self.__start:
            self.__start = Icon.new_icon_from_icon_names([gtk.STOCK_MEDIA_PLAY, "player_play"], self._size)
        return self.__start

    @property
    def ticking(self):
        if not self.__ticking:
            self.__ticking = Icon.new_icon_from_icon_names(["appointment-soon"], self._size)
        return self.__ticking

    @property
    def coffeebreak(self):
        if not self.__coffeebreak:
            self.__coffeebreak = Icon.new_icon_from_file(config.tools_path + "/icons/coffee_break.svg", self._size)
        return self.__coffeebreak

    @property
    def pause(self):
        if not self.__pause:
            self.__pause = Icon.new_icon_from_icon_names([gtk.STOCK_MEDIA_PAUSE, "player_pause"], self._size)
        return self.__pause

    @property
    def priority(self):
        if not self.__priority:
            self.__priority = [Icon.new_icon_from_file(config.tools_path + "/icons/priori_0.svg", self._size),
                               Icon.new_icon_from_file(config.tools_path + "/icons/priori_1.svg", self._size),
                               Icon.new_icon_from_file(config.tools_path + "/icons/priori_2.svg", self._size),
                               Icon.new_icon_from_file(config.tools_path + "/icons/priori_3.svg", self._size)]
        return self.__priority

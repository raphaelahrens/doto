"""The icon module is used by the Done!Tools to load icons."""

import gtk

import config

_THEME = gtk.icon_theme_get_default()


class Icon(object):

    """Icon class which stores the Pixbuf and the file name."""

    def __init__(self, filename, pixbuf):
        """
        The Constructor for the Icon class.

        @param filename the full path to the file of the icon.
        @param pixbuf the Pixbuf object that

        """
        self.__filename = filename
        self.__pixbuf = pixbuf

    @staticmethod
    def new_icon_from_file(filename, size):
        """
        Construct a new  Icon object from a file.

        The volume of the Icon ist size*size

        @param filename The full path to the file of the icon
        @param The size of the Icon.

        @return a new Icon object

        """
        return Icon(filename, gtk.gdk.pixbuf_new_from_file_at_size(filename, size, size))

    @staticmethod
    def new_icon_from_icon_names(icon_names, size):
        """
        Construct an new Icon object from a list of GTK icon names.

        @param icon_names A List of names for the icon

        @return a new Icon object

        """
        icon_info = _THEME.choose_icon(icon_names, size, 0)
        return Icon(icon_info.get_filename(), icon_info.load_icon())

    @property
    def filename(self):
        """
        Getter for the filename of the Icon.

        @return the file name as a string

        """
        return self.__filename

    @property
    def pixbuf(self):
        """
        The getter for the Pixbuf of the Icon.

        @return the Pixbuf object associated with the Icon

        """
        return self.__pixbuf


class Theme(object):

    """
    The theme class for the Done!Tools.

    It holds all the Icons which are used by the Done!Tools

    """

    def __init__(self, size):
        """
        Create a new theme with the icon size equal to size.

        @param size The size of the Icons for the theme

        """
        self._size = size
        self.__start = None
        self.__ticking = None
        self.__coffeebreak = None
        self.__pause = None
        self.__priority = None
        self.__created = None
        self.__due = None
        self.__done = None

    @property
    def start(self):
        """
        Getter for the start Icon.

        @return the start icon

        """
        if not self.__start:
            self.__start = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/play.svg", self._size)
        return self.__start

    @property
    def ticking(self):
        """
        Getter for the ticking Icon.

        @return the ticking icon

        """
        if not self.__ticking:
            self.__ticking = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/ticking.svg", self._size)
        return self.__ticking

    @property
    def coffeebreak(self):
        """
        Getter for the coffeebreak Icon.

        @return the coffeebreak icon

        """
        if not self.__coffeebreak:
            self.__coffeebreak = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/coffee_break.svg", self._size)
        return self.__coffeebreak

    @property
    def pause(self):
        """
        Getter for the pause Icon.

        @return the pause icon

        """
        if not self.__pause:
            self.__pause = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/pause.svg", self._size)
        return self.__pause

    @property
    def priority(self):
        """
        Getter for the priority Icon.

        @return the priority icons

        """
        if not self.__priority:
            self.__priority = []
            for f_str in ["./icons/priori_0.svg",
                          "./icons/priori_1.svg",
                          "./icons/priori_2.svg",
                          "./icons/priori_3.svg"]:
                self.__priority.append(Icon.new_icon_from_file(config.TOOLS_PATH + f_str, self._size))
        return self.__priority

    @property
    def created(self):
        """
        Getter for the created Icon.

        @return the created icon

        """
        if not self.__created:
            self.__created = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/created.svg", self._size)
        return self.__created

    @property
    def due(self):
        """
        Getter for the due Icon.

        @return the due icon

        """
        if not self.__due:
            self.__due = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/due.svg", self._size)
        return self.__due

    @property
    def done(self):
        """
        Getter for the done Icon.

        @return the done icon

        """
        if not self.__done:
            self.__done = Icon.new_icon_from_file(config.TOOLS_PATH + "/icons/done.svg", self._size)
        return self.__done

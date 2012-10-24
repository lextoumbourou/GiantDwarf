from time import sleep
from datetime import datetime
import sys
import pkgutil
import os
import logging

from pyfire import Campfire
from BeautifulSoup import BeautifulSoup

import settings

class GiantDwarf():
    """
    GiantDwarf class manages loading plugins and providing 
    an interface for the pyfire class

    """
    def __init__(self):
        self.plugins = []
        self.is_connected = False
        self.room = None;

        self.load_all_plugins()

    def _get_class_name(self, mod_name):
        """Return the class name from a plugin name"""
        output = ""

        # Split the _ and ignore the 1st word plugin
        words = mod_name.split('_')[1:]

        # Capitalise the first letter of each word and add to string
        for word in words:
            output += word.title()

        return output

    def load_all_plugins(self):
        path = os.path.join(os.path.dirname(__file__), 'plugins')
        modules = pkgutil.iter_modules(path=[path])

        for loader, mod_name, ispkg in modules:
            # Ensure that module isn't already loaded
            if mod_name not in sys.modules:
                # import module
                loaded_mod = __import__(path+"."+mod_name, fromlist=[mod_name])

                # load class from imported module
                class_name = self._get_class_name(mod_name)
                loaded_class = getattr(loaded_mod, class_name)

                # create an instance of the class
                self.plugins.append(loaded_class())

    def start_campfire(self):
        """
        Return a room object
        """
        # Setup Campfire and join our room
        c = Campfire(settings.SUBDOMAIN,
                     settings.TOKEN,
                     'x',
                     ssl=settings.USE_SSL)
        self.is_connected = True
        self.room = c.get_room_by_name(settings.ROOM)

class GiantDwarfPlugin():
    """
    Each plugin should be a subclass of this
    """
    def run(self):
        pass

if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(format="%(asctime)-15s %(message)s",
                        filename=settings.LOG_FILE,
                        level=logging.INFO)
    # Ensure we don't get old Nagios events
    last_run = datetime.now()
    logging.info("Online and ready")
    gd = GiantDwarf()

    while True:
        if not gd.is_connected:
            gd.start_campfire()
            gd.room.join()
        try:
            last_run = datetime.now()
            for plugin in gd.plugins:
                plugin.run(gd)
            logging.info("Last message @ {0}".format(last_run))
        except KeyboardInterrupt:
            logging.info("Leaving the room")
            gd.room.leave()
            exit()
        except Exception, e:
            # I don't want GiantDwarf dying over an exception
            # this allows it to pass and try again next period
            logging.warning("Exception occured: ", e)
            gd.is_connected = False

        sleep(settings.FETCH_INTERVAL)

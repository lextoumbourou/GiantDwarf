from time import sleep
from datetime import datetime
import sys
import pkgutil
import os
import logging

from pyfire import Campfire
from BeautifulSoup import BeautifulSoup

import settings

GD_NAMES = ("GiantDwarf", "GD", "gd")

class GiantDwarf():
    """
    GiantDwarf class manages loading plugins and providing 
    an interface for the pyfire class
    """

    def __init__(self):
        """
        Init method loads all the plugins preparing the class
        """
        self.passive_plugins = []
        self.active_plugins = {}
        self.is_connected = False
        self.room = None;

        self._load_plugins()

        # Configure logging
        self.logging = logging
        self.logging.basicConfig(
                format="%(asctime)-15s %(message)s",
                filename=settings.LOG_FILE,
                level=logging.INFO)


    def _load_class(self, plugin, class_name):
        """
        Return a class for instantiation from a module name
        """
        loaded_mod = __import__(plugin, fromlist=[plugin])
        return getattr(loaded_mod, class_name)

    def _load_plugins(self):
        """
        Load all plugins defined in the settings file populating the 
        self.active_plugins and self.passive_plugins attributes
        """
        # Load passive plugins into a list
        for plugin, class_name in settings.PASSIVE_PLUGINS:
            loaded_class = self._load_class(plugin, class_name)
            # create an instance of the class
            self.passive_plugins.append(loaded_class())

        # Load active plugins into a dict
        for plugin, class_name in settings.ACTIVE_PLUGINS:
            loaded_class = self._load_class(plugin, class_name) 
            # Just get the module name for use in the active plugin key
            module = plugin.split('.')[-1]
            # create an instance of the class
            self.active_plugins[module] = loaded_class()


    def _start_campfire(self):
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
        self.room.join()

        # Attach to active stream 
        stream = self.room.get_stream(live=False)
        stream.attach(self._process_messages).start()


    def _process_messages(self, message):
        """
        Handles processing data sent from the room
        """
        user = ""
        if message.is_text():
            if message.body.startswith(GD_NAMES):
                try:
                    body = message.body.split(" ")
                    data = []
                    if len(body) > 1:
                        plugin_name = body[1]

                    if len(body) > 2:
                        data = body[2:]
                    reply = plugin_name
                    try:
                        self.active_plugins[plugin_name].run(data, self.room)
                    except KeyError:
                        self.room.speak("Hmmm...I don't know what that means...")
                except IndexError:
                    reply = "Erm...what?"


    def start(self):
        """
        Main function that handles starting Campfire and 
        running passive checks
        """
        self.last_run = datetime.now()
        self.logging.info("Online and ready")

        while True:
            if not self.is_connected:
                self._start_campfire()
                self.logging.info("Attached and ready to roll!")
            try:
                self.last_run = datetime.now()
                # Run passive checks
                for plugin in self.passive_plugins:
                    if plugin.should_run():
                        self.logging.debug("Running plugin " + str(plugin)) 
                        plugin.run(self.room)

                self.logging.info("Last message @ {0}".format(self.last_run))
            except KeyboardInterrupt:
                self.logging.info("Leaving the room")
                self.room.leave()
                exit()
            except Exception, e:
                # I don't want GiantDwarf dying over an exception
                # this allows it to pass and try again next period
                self.logging.warning("Exception occured: " + e)
                self.is_connected = False

            sleep(1)
                

class GiantDwarfPlugin(object):
    """
    Each passive plugin should be a subclass of this
    """
    def __init__(self):
        # Can be overwritten by subclasses to change interval
        self.interval = settings.FETCH_INTERVAL

    def should_run(self):
        """
        Determine if plugin should be run based on interval settings
        """
        try:
            self.interim_interval += 1
        except AttributeError:
            self.interim_interval = 0

        if self.interim_interval == self.interval:
            self.interim_interval = 0
            return True

        return False


    def run(self):
        pass


if __name__ == '__main__':
    gd = GiantDwarf()
    gd.start()

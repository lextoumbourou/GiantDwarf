from time import sleep
from datetime import datetime
import sys
import pkgutil
import os
import re
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
        self.message_re = re.compile('\S+\s+(?P<plugin>\S+)\s+(?P<action>\S+)\s+(?P<data>.*)')

        # Configure logging
        self.logging = logging
        self.logging.basicConfig(
                format="%(asctime)-15s %(message)s",
                filename=settings.LOG_FILE,
                level=logging.INFO)
    

    def _get_class_name(self, mod_name):
        """
        Return the class name from a plugin name
        """
        output = ""

        # Split the _ and ignore the 1st word plugin
        words = mod_name.split('_')[1:]

        # Capitalise the first letter of each word and add to string
        for word in words:
            output += word.title()

        return output


    def _load_passive_plugins(self):
        """
        Iterate through the plugin directory and attempt to load all those
        plugins that begin with plugin_passive_
        """
        path = os.path.join(os.path.dirname(__file__), 'plugins')
        modules = pkgutil.iter_modules(path=[path])

        for loader, mod_name, ispkg in modules:
            # Ensure that module isn't already loaded
            if (mod_name not in sys.modules and 
                mod_name.startswith('passive')):
                # import module
                loaded_mod = __import__(path+"."+mod_name, fromlist=[mod_name])

                # load class from imported module
                class_name = self._get_class_name(mod_name)
                loaded_class = getattr(loaded_mod, class_name)

                # create an instance of the class
                self.passive_plugins.append(loaded_class(self.room))

    def _load_active_plugins(self):
        """
        Iterate through the plugin directory and attempt to load all those
        plugins that begin with plugin_passive_
        """
        path = os.path.join(os.path.dirname(__file__), 'plugins')
        modules = pkgutil.iter_modules(path=[path])

        for loader, mod_name, ispkg in modules:
            # Ensure that module isn't already loaded
            if (mod_name not in sys.modules and 
                mod_name.startswith('active')):
                # import module
                loaded_mod = __import__(path+"."+mod_name, fromlist=[mod_name])

                # load class from imported module
                class_name = self._get_class_name(mod_name)
                loaded_class = getattr(loaded_mod, class_name)

                # create an instance of the class
                self.active_plugins[mod_name] = loaded_class(self.room)


    def _start_campfire(self):
        """
        Connect to campfire and load plugins
        """
        # Setup Campfire and join our room
        c = Campfire(settings.SUBDOMAIN, settings.TOKEN, 'x',
                     ssl=settings.USE_SSL)
        self.is_connected = True
        self.room = c.get_room_by_name(settings.ROOM)
        self.room.join()

        # Load the plugins
        self._load_passive_plugins()
        self._load_active_plugins()

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
                    
                    message = self.message_re.match(message.body)
                    
                    plugin = message.group('plugin')
                    action = message.group('action')
                    data = message.group('data')

                    self.room.speak('i got plugin ' + plugin)
                    self.room.speak('i got action ' + action)
                    self.room.speak('i got data ' + data)
                    reply = plugin
                    
                    #try:
                    self.active_plugins["active_" + plugin].run(action, data)
                    #except KeyError:
                    #    pass
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
                self.room.speak('Attached and ready to roll!')
            try:
                self.last_run = datetime.now()
                # Run passive checks
                for plugin in self.passive_plugins:
                    if plugin.should_run():
                        self.logging.debug("Running plugin " + str(plugin)) 
                        plugin.run()

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
    def __init__(self, room):
        # Can be overwritten by subclasses to change interval
        self.interval = settings.FETCH_INTERVAL
        self._room = room
        self.create()

    def create(self):
        """
        The user-friendly constructor which plugins may override to perform
        initial tasks required by the plugin
        """
        pass

    def speak(self, data):
        self._room.speak(data)

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

    def run(self, action, data):
        pass


if __name__ == '__main__':
    gd = GiantDwarf()
    gd.start()

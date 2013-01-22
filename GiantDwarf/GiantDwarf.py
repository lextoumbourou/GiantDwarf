from time import sleep
from datetime import datetime
import sys
import pkgutil
import os
import re
import logging
import ConfigParser

from pyfire import Campfire
from BeautifulSoup import BeautifulSoup

GD_NAMES = ("GiantDwarf", 'giantdwarf', "GD", "gd")


class RawConfigParserUpper(ConfigParser.RawConfigParser):
    """
    Overwriting the parent config parser to allow
    uppercase config parameters as per docs
    """
    def optionxform(self, optionstr):
        return optionstr


def load_config():
    """
    Search for the giantdwarf.conf file in the following order:
    1. Current directory,
    2. Process owner's home path,
    3. /etc/giantdwarf/,
    4. Location specified in the GIANTDWARF_CONF environment variable
    Variables in configs found later will overwrite those found earlier
    """
    config = RawConfigParserUpper()

    for location in (
            os.curdir, "/etc/giantdwarf/",  
            os.path.expanduser("~"), os.environ.get("GIANTDWARF_CONF")):
        if location:
            try: 
                with open(os.path.join(location, "giantdwarf.conf")) as source:
                    config.readfp(source)
            except IOError:
                pass
    return config


def parse_config():
    """
    Returns a dictionary containing config parameters
    or causes the program to exit()
    """
    config = load_config()

    if not config.get('Campfire', 'token'):
        print 'Token not found in giantdwarf.conf'
        return False

    if not config.get('Campfire', 'subdomain'):
        print 'Subdomain not found in giantdwarf.conf'
        return False

    if not config.get('Campfire', 'room'):
        print 'Room not found in giantdwarf.conf'
        return False

    # If they haven't specified a log file location, 
    # put it somewhere sensible
    if not config.get('General', 'log_file'):
        config.set('General', 'log_file', '/var/log/giantdwarf.log')

    # Same for use_ssl
    if not config.get('Campfire', 'use_ssl'):
        config.set('Campfire', 'use_ssl', 'yes')

    return config


def load_class(plugin, class_name):
    """
    Return a class for instantiation from a module name
    """
    loaded_mod = __import__(plugin, fromlist=[plugin])
    return getattr(loaded_mod, class_name)


class GiantDwarf():
    """
    GiantDwarf class manages loading plugins and providing
    an interface for the pyfire class
    """
    def __init__(self, config):
        """
        Init method loads all the plugins preparing the class
        """
        self.config = config
        self.is_connected = False
        self.passive_plugins = []
        self.active_plugins = {}
        self.room = None
        self.message_re = re.compile(
            '\S+\s+(?P<plugin>\S+)\s+(?P<action>\S+)\s+(?P<data>.*)')

        # Configure logging
        self.logging = logging
        if self.config.get('General', 'log_mode') == 'debug':
            level = logging.DEBUG
        else:
            level = logging.INFO

        self.logging.basicConfig(
            format="%(asctime)-15s %(message)s",
            filename=self.config.get('General', 'log_file'),
            level=level)

    
    def _load_plugins(self):
        """
        Load all plugins defined in the config file populating the
        self.active_plugins and self.passive_plugins attributes
        """
        # Load passive plugins into a list
        for class_name, plugin in self.config.items('Passive Plugins'):
            loaded_class = load_class(plugin, class_name)
            # create an instance of the class
            self.passive_plugins.append(loaded_class(self.room, config))

        # Load active plugins into a dict
        for class_name, plugin in self.config.items('Active Plugins'):
            loaded_class = load_class(plugin, class_name)
            # Just get the module name for use in the active plugin key
            module = plugin.split('.')[-1]
            # create an instance of the class
            self.active_plugins[module] = loaded_class(self.room, config)

    def _start_campfire(self):
        """
        Connect to campfire and load plugins
        """
        # Setup Campfire and join our room
        campfire = Campfire(
            self.config.get('Campfire', 'subdomain'), 
            self.config.get('Campfire', 'token'), 'x', 
            ssl=self.config.getboolean('Campfire', 'use_ssl'))
        self.is_connected = True
        self.room = campfire.get_room_by_name(
            self.config.get('Campfire', 'room'))
        self.room.join()
        self._load_plugins()

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
                print message.body
                message = self.message_re.match(message.body)
                plugin = message.group('plugin')
                action = message.group('action')
                data = message.group('data')

                try:
                    self.active_plugins[plugin].run(action, data)
                except KeyError:
                    self.room.speak('Unable to find plugin ' + plugin)

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

                self.logging.debug("Last message @ {0}".format(self.last_run))
            except KeyboardInterrupt:
                self.logging.info("Leaving the room")
                self.room.leave()
                exit()
            except Exception, e:
                # I don't want GiantDwarf dying over an exception
                # this allows it to pass and try again next period
                self.logging.warning("Exception occured: " + e)

            sleep(1)


class GiantDwarfPlugin(object):
    """
    Each passive plugin should be a subclass of this
    """
    def __init__(self, room, config):
        # Can be overwritten by subclasses to change interval
        self.interval = 30 
        self.config = config
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
    config = parse_config()
    if not config:
        exit()

    gd = GiantDwarf(config)
    gd.start()

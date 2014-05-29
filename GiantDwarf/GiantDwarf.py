from time import sleep
from sys import exit

from datetime import datetime

from lib.helpers import load_class


class GiantDwarf(object):
    def __init__(self, config, conn):
        self.config = config
        self.conn = conn
        self.plugins = []

    def _load_plugins(self):
        for class_path in self.config.get('plugins', []):
            class_name = class_path.split('.')[-1]
            module = '.'.join(class_path.split('.')[:2])
            loaded_class = load_class(module, class_name)
            plugin_config = self.config[class_name.lower()]
            self.plugins.append(
                loaded_class(self.conn, plugin_config)
            )

    def start(self):
        last_run = datetime.now()
        if not self.plugins:
            self._load_plugins()
        while True:
            try:
                for plugin in self.plugins:
                    if plugin.should_run():
                        plugin.run()
            except KeyboardInterrupt:
                exit()

            sleep(1)

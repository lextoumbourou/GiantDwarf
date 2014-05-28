class GiantDwarf(object):
    def __init__(self, config, conn):
        self.config = config
        self.conn = conn
        self.plugins = []

    def _load_plugins(self):
        for class_name, plugin in self.config.get('plugins', [])
            loaded_class = load_class(plugin, class_name)
            config = self.config[plugin]
            self.plugins.append(loaded_class(self.conn, config))

    def start(self):
        last_run = datetime.now()
        while True:
            try:
                for plugin in self.plugins:
                    plugin.run()
            except KeyboardInterrupt:
                pass

            sleep(1)

class GiantDwarfBasePlugin(object):
    """
    Each passive plugin should be a subclass of this
    """
    def __init__(self, conn, config):
        self.interim_interval = 0
        # Can be overwritten by subclasses to change interval
        self.interval = 5 # in seconds
        self.config = config
        self.conn = conn
        self.create()

    def create(self):
        """
        The user-friendly constructor which plugins may override to perform
        initial tasks required by the plugin
        """
        pass

    def should_run(self):
        """
        Determine if plugin should be run based on interval settings
        """
        self.interim_interval += 1

        if self.interim_interval == self.interval:
            self.interim_interval = 0
            return True

        return False

    def run(self, action, data):
        pass

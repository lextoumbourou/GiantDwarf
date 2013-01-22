from GiantDwarf import GiantDwarfPlugin


class Say(GiantDwarfPlugin):
    def run(self, action, data):
        self.speak(action + " " + data)

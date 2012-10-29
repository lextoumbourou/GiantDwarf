from GiantDwarf import GiantDwarfPlugin
import settings

class Say(GiantDwarfPlugin):
    def run(self, action, data):
        self.speak(action + " " + data)

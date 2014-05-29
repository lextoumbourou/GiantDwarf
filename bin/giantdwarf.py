#!/usr/bin/env python
import yaml
from slacker import Slacker

from GiantDwarf import GiantDwarf


if __name__ == '__main__':
    config = yaml.load(open('config.yaml'))
    if not config:
        exit()

    connection = Slacker(config.get('token'))

    giantdwarf = GiantDwarf(config, connection)
    giantdwarf.start()

#!/usr/bin/env python
import yaml
from slacker import Slacker

from .lib import GiantDwarf
from .lib.helpers import parse_config

if __name__ == '__main__':
    config = yaml.load('config.yaml')

    connection = Slacker(config['slack'].get('token'))
    slack = GiantDwarf(config, connection)
    if not config:
        exit()

    giantdwarf = GiantDwarf(config)
    giantdwarf.start()

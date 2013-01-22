#!/usr/bin/env python

from GiantDwarf.GiantDwarf import GiantDwarf, parse_config

if __name__ == '__main__':
    config = parse_config()
    if not config:
        exit()

    giantdwarf = GiantDwarf(config)
    giantdwarf.start()
    main()

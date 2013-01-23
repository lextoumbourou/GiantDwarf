#!/usr/bin/env python

from distutils.core import setup

setup(name='GiantDwarf',
      version='0.5',
      description='A simple Campfire bot written in Python',
      author='Lex Toumbourou',
      author_email='lextoumbourou@gmail.com',
      url='http://github.com/lextoumbourou/GiantDwarf',
      requires=['BeautifulSoup'],
      packages=['GiantDwarf', 'GiantDwarf.plugins', 'GiantDwarf.lib'],
      scripts=['bin/giantdwarf.py'],)

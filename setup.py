#!/usr/bin/env python

from distutils.core import setup

setup(name='GiantDwarf',
      version='0.2',
      description='A simple Campfire bot written in Python',
      author='Lex Toumbourou',
      author_email='lextoumbourou@gmail.com',
      url='http://github.com/lextoumbourou/GiantDwarf',
      requires=['BeautifulSoup'],
      packages=['GiantDwarf'],
      scripts=['bin/giantdwarf.py'],)

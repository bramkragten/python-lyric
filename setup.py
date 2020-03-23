#!/usr/bin/env python
# -*- coding:utf-8 -*-

import io

from setuptools import setup


version = '1.1.6'


setup(name='python-lyric',
      version=version,
      description='Python API for talking to the '
                  'Honeywell Lyric™ Thermostat',
      long_description=io.open('README.rst', encoding='UTF-8').read(),
      keywords='honeywell lyric thermostat',
      author='Bram Kragten',
      author_email='mail@bramkragten.nl',
      url='https://github.com/bramkragten/python-lyric/',
      packages=['lyric'],
      install_requires=['requests>=1.0.0',
                        'requests_oauthlib>=0.7.0']
      )

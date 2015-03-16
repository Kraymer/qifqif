#!/usr/bin/env python

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import os
import sys

from setuptools import setup


def publish():
    """Publish to PyPi"""
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

setup(name='qifqif',
    version='0.1.0.post1',
    description='QIF file editing tool',
    long_description=open('README.rst').read(),
    author='Fabrice Laporte',
    author_email='kraymer@gmail.com',
    url='https://github.com/KraYmer/qifqif',
    license='MIT',
    platforms='ALL',

    packages=[
      'qifqif',
    ],

    entry_points={
      'console_scripts': [
          'qifqif = qifqif:main',
      ],
    },


    classifiers=[
      'License :: OSI Approved :: MIT License',
      'Programming Language :: Python',
      'Environment :: Console',
      'Topic :: Office/Business :: Financial :: Accounting'
    ])

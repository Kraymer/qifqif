#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import codecs
import os
import re
import sys
import time
from setuptools import setup

PKG_NAME = "qifqif"
DIRPATH = os.path.dirname(__file__)


def read_rsrc(filename):
    with codecs.open(os.path.join(DIRPATH, filename), encoding="utf-8") as _file:
        return re.sub(r":(\w+\\?)+:", u"", _file.read().strip())  # no emoji


with codecs.open("cronicle/__init__.py", encoding="utf-8") as fd:
    version = re.search(
        r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fd.read(), re.MULTILINE
    ).group(1)
    version = version.replace("dev", str(int(time.time())))

setup(name=PKG_NAME,
    version=version,
    description='Enrich your QIF files with categories',
    long_description=open('README.md').read(),
    author='Fabrice Laporte',
    author_email='kraymer@gmail.com',
    url='https://github.com/KraYmer/qifqif',
    license='MIT',
    platforms='ALL',
    packages=['qifqif', ],
    entry_points={
        'console_scripts': [
            'qifacc = qifqif.qifacc:main',
            'qifqif = qifqif:main',
        ],
    },
    install_requires=['argparse', 'ordereddict', 'pyyaml'] + (
        ['pyreadline', 'colorama'] if sys.platform == 'win32' else
        ['blessed']) + (
        ['gnureadline'] if sys.platform == 'darwin' else []),
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Environment :: Console',
        'Topic :: Office/Business :: Financial :: Accounting'
    ]
)

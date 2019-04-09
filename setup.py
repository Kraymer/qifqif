#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import sys
from setuptools import setup

exec(open('qifqif/_version.py').read())

setup(name='qifqif',
    version=__version__,
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

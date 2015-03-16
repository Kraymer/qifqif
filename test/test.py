#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Units tests"""

import os
import tempfile
import shutil
import unittest
import json

import qifqif

CONFIG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                           'rsrc', 'config.json')


class TestQifQif(unittest.TestCase):

    def setUp(self):
        print 'yo'
        with open(CONFIG_FILE, 'r') as cfg:
            tags = json.load(cfg)
        self.tags = tags
        self.payee = 'CARTE 16/02/2014 Sully bar'

    def test_find_tag(self):
        self.assertTrue(qifqif.find_tag(self.tags, 'Sully'), 'Bars')

    def test_is_match(self):
        self.assertTrue(qifqif.is_match('sully bar', self.payee))

    def test_update_config(self):
        dest = os.path.join(tempfile.mkdtemp(), os.path.basename(CONFIG_FILE))
        shutil.copy2(CONFIG_FILE, dest)
        qifqif.update_config(dest, 'Bars', 'Sully', 'Drink', 'Sully')
        with open(dest, 'r') as cfg:
            new_cfg = json.load(cfg)
            self.assertTrue('Sully' in new_cfg['Drink'] and
                            'Sully' not in new_cfg['Bars'])

if __name__ == '__main__':
    unittest.main()

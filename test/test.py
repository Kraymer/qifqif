#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Units tests"""

import os
import shutil
import tempfile
import unittest

from qifqif import tags

CONFIG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                           'rsrc', 'config.json')


class TestQifQif(unittest.TestCase):

    def setUp(self):
        tags.load(CONFIG_FILE)
        self.payee = 'CARTE 16/02/2014 Sully bar'

    def test_find_tag(self):
        self.assertTrue(tags.find_tag_for('Sully'), 'Bars')

    def test_is_match(self):
        self.assertTrue(tags.is_match('sully bar', self.payee))

    def test_update_config(self):
        dest = os.path.join(tempfile.mkdtemp(), os.path.basename(CONFIG_FILE))
        shutil.copy2(CONFIG_FILE, dest)
        tags.edit(dest, 'Bars', 'Sully', 'Drink', 'Sully')


if __name__ == '__main__':
    unittest.main()

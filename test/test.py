#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Units tests"""

import os
import shutil
import tempfile
import unittest

import qifqif
from qifqif import tags

CONFIG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                           'rsrc', 'config.json')
QIF_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', 'transac01.qif')


class TestQifQif(unittest.TestCase):

    def setUp(self):
        tags.load(CONFIG_FILE)
        self.transaction = qifqif.create_transaction(
            zip(['payee'], ['CARTE 16/02/2014 Sully bar']))

    def test_find_tag(self):
        self.assertTrue(tags.find_tag_for('Sully'), 'Bars')

    def test_is_match(self):
        self.assertTrue(tags.is_match('sully bar', self.transaction['payee']))

    def test_update_config(self):
        dest = os.path.join(tempfile.mkdtemp(), os.path.basename(CONFIG_FILE))
        shutil.copy2(CONFIG_FILE, dest)
        # Replace 'Sully' match tag from 'Bars' to 'Drink'
        tags.edit(dest, 'Bars', 'Sully', 'Drink', 'Sully')
        tags.load(dest)
        self.assertTrue(tags.find_tag_for('Sully'), 'Drink')

    def test_dump_to_file(self):
        dest = os.path.join(tempfile.mkdtemp(), os.path.basename(CONFIG_FILE))
        qifqif.dump_to_file(dest, [self.transaction])
        with open(dest) as dst:
            dest_content = dst.read().strip()
        with open(QIF_FILE) as qif:
            qif_content = qif.read().strip()
        self.assertEqual(dest_content, qif_content)

if __name__ == '__main__':
    unittest.main()

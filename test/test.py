#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Units tests"""

import os
import shutil
import tempfile
import unittest

from mock import patch
from yaml import load

import qifqif
from qifqif import tags

CONFIG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                           'rsrc', 'config.json')
QIF_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', 'transac.qif')
with open(os.path.join(os.path.realpath(os.path.dirname(__file__)),
          'rsrc', 'transac.yaml')) as f:
    TEST_DATA = load(f)


def rsrc_path(fname):
    return os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', fname)


def mock_input_default(prompt, choices=''):
    res = [x for x in choices if x.isupper()][0]
    return res


def mock_input_edit_category(prompt, choices=''):
    if prompt.startswith('Edit'):
        return 'Y'
    if prompt.startswith('Category'):
        return 'Drink'
    if prompt.startswith('Match'):
        return 'Sully'
    if prompt.endswith('Continue'):
        return 'Y'


class TestPayeeTransaction(unittest.TestCase):

    def setUp(self):
        tags.load(CONFIG_FILE)
        self.transaction = qifqif.parse_file(TEST_DATA['t01_notag']['raw'])

    def test_find_tag(self):
        self.assertTrue(tags.find_tag_for('Sully'), 'Bars')

    def test_is_match(self):
        self.assertTrue(tags.is_match('sully bar',
                                      self.transaction[0]['payee']))

    def test_update_config(self):
        dest = os.path.join(tempfile.mkdtemp(), os.path.basename(CONFIG_FILE))
        shutil.copy2(CONFIG_FILE, dest)
        # Replace 'Sully' match tag from 'Bars' to 'Drink'
        tags.edit('Bars', 'Sully', 'Drink', 'Sully', {'config': dest})
        tags.load(dest)
        self.assertTrue(tags.find_tag_for('Sully'), 'Drink')

    def test_parse_args(self):
        self.assertEqual(qifqif.parse_args(['qifqif', '-a', '-b', 'in.qif']),
                         False)
        args = qifqif.parse_args(['qifqif', QIF_FILE])
        self.assertTrue(args['dest'], args['src'])

    def test_parse_file(self):
        self.assertEqual(len(self.transaction), 1)
        self.assertEqual(self.transaction[0]['payee'],
                         TEST_DATA['t01_notag']['fields']['payee'])


class TestFullTransaction(unittest.TestCase):

    def setUp(self):
        tags.load(CONFIG_FILE)
        self.transactions = qifqif.parse_file(TEST_DATA['t02']['raw'],
                                              {'batch': True})

    def test_process_file(self):
        res = qifqif.process_file(self.transactions, {'config': CONFIG_FILE})
        self.assertEqual(len(res), 2)
        self.assertEqual(res[1]['category'], 'Bars')

    def test_dump_to_file(self):
        dest = os.path.join(tempfile.mkdtemp(),
                            str(tempfile._get_candidate_names()))
        res = qifqif.dump_to_file(dest, self.transactions, {'batch': True})
        with open(dest) as dst:
            dest_content = dst.read().strip()
        with open(QIF_FILE) as qif:
            qif_content = qif.read().strip()
        self.assertEqual(dest_content, qif_content)
        self.assertEqual(res, qif_content)

    @patch('qifqif.quick_input', side_effect=mock_input_default)
    def test_audit_mode_no_edit(self, mock_quick_input):
        res = qifqif.process_file(self.transactions, {'config': CONFIG_FILE,
                                  'audit': True})
        self.assertEqual(len(res), 2)
        self.assertEqual(res[1]['category'], 'Bars')

    @patch('qifqif.quick_input', side_effect=mock_input_edit_category)
    def test_audit_mode(self, mock_quick_input):
        res = qifqif.process_file(self.transactions,
                                  {'config': CONFIG_FILE, 'audit': True,
                                   'dry-run': True})
        self.assertEqual(len(res), 2)
        self.assertEqual(res[1]['category'], 'Drink')

    @patch('sys.argv', ['qifqif', '-c', CONFIG_FILE, '-b',
           os.path.join(os.path.realpath(os.path.dirname(__file__)), 'rsrc',
                        'transac.qif')])
    def test_main(self):
        res = qifqif.main()
        self.assertEqual(res, 0)

if __name__ == '__main__':
    unittest.main()

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
from qifqif import ui

CONFIG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                           'rsrc', 'config.json')
QIF_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', 'transac.qif')
CURRENT_DIR = os.path.realpath(os.path.dirname(__file__))
with open(os.path.join(os.path.realpath(os.path.dirname(__file__)),
          'rsrc', 'transac.yaml')) as f:
    TEST_DATA = load(f)
KEYBOARD_INPUTS = ['Y', 'Drink', 'Sully']


def rsrc_path(fname):
    return os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', fname)


def mock_input_default(prompt, choices=''):
    res = [x for x in choices if x.isupper()]
    return res[0] if res else ''


def get_data(fpath, as_lines=False):
    with open(fpath) as f:
        if as_lines:
            content = f.readlines()
        else:
            content = f.read()
    return content


class TestPayeeTransaction(unittest.TestCase):

    def setUp(self):
        tags.load(CONFIG_FILE)
        self.transaction = qifqif.parse_file(TEST_DATA['t01_notag']['raw'])

    def test_find_tag(self):
        self.assertEqual(tags.find_tag_for('Sully')[0], 'Bars')
        self.assertEqual(tags.find_tag_for('Sullyz')[0], None)
        self.assertEqual(tags.find_tag_for('Shop Art Brut Denim')[0],
                         'Clothes')

    def test_is_match(self):
        self.assertTrue(tags.is_match('sully bar',
                                      self.transaction[0]['payee']))

    def test_update_config(self):
        dest = os.path.join(tempfile.mkdtemp(), os.path.basename(CONFIG_FILE))
        shutil.copy2(CONFIG_FILE, dest)
        # Replace 'Sully' match tag from 'Bars' to 'Drink'
        tags.edit('Bars', 'Sully', 'Drink', 'Sully', {'config': dest})
        tags.load(dest)
        self.assertEqual(tags.find_tag_for('Sully')[0], 'Drink')

    def test_parse_args(self):
        self.assertFalse(qifqif.parse_args(['qifqif', '-a', '-b', 'in.qif']))
        args = qifqif.parse_args(['qifqif', QIF_FILE])
        self.assertEqual(args['dest'], args['src'])

    def test_parse_file(self):
        self.assertEqual(len(self.transaction), 1)
        self.assertEqual(self.transaction[0]['payee'],
                         TEST_DATA['t01_notag']['fields']['payee'])

    def test_completer(self):
        self.assertEqual(set(ui.complete_matches('A: B,C')), set(['A',
                         'A: B,C', 'B', 'B,C', 'C']))

TEMP_DIR = tempfile.mkdtemp()
CONFIG_TEST_FILE = os.path.join(TEMP_DIR, 'config.json')
QIF_TEST_FILE = os.path.join(TEMP_DIR, 'transac.qif')


class TestFullTransaction(unittest.TestCase):

    def setUp(self):
        tags.load(CONFIG_FILE)
        self.transactions = qifqif.parse_file(TEST_DATA['t02']['raw'],
                                              {'batch': True})
        shutil.copyfile(CONFIG_FILE, CONFIG_TEST_FILE)
        shutil.copyfile(QIF_FILE, QIF_TEST_FILE)

    @patch('qifqif.quick_input', side_effect=mock_input_default)
    def test_parse_file_continue(self, mock_quick_input):
        transactions = qifqif.parse_file(TEST_DATA['t02']['raw'])
        self.assertEqual(len(transactions), 3)

    @patch('qifqif.quick_input', side_effect=[''])
    def test_process_file(self, mock_quick_input):
        res = qifqif.process_file(self.transactions, {'config':
                                  CONFIG_TEST_FILE})
        self.assertEqual(len(res), 3)
        self.assertEqual(res[1]['category'], 'Bars')

    def test_dump_to_buffer(self):
        res = qifqif.dump_to_buffer(self.transactions)
        self.assertEqual(res, get_data(QIF_FILE))

    @patch('qifqif.quick_input', side_effect=mock_input_default)
    def test_audit_mode_no_edit(self, mock_quick_input):
        res = qifqif.process_file(self.transactions, {'config':
                                  CONFIG_TEST_FILE,
                                  'audit': True})
        self.assertEqual(len(res), 3)
        self.assertEqual(res[1]['category'], 'Bars')

    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS + ['', ''])
    def test_audit_mode(self, mock_quick_input):
        res = qifqif.process_file(self.transactions,
                                  {'config': CONFIG_FILE, 'audit': True,
                                   'dry-run': True})
        self.assertEqual(len(res), 3)
        self.assertEqual(res[1]['category'], 'Drink')

    @patch('sys.argv', ['qifqif', '-c', CONFIG_TEST_FILE, '-b', '-d',
           QIF_FILE])
    def test_main(self):
        res = qifqif.main()
        self.assertEqual(res, 0)

    @patch('sys.argv', ['qifqif', '-c', CONFIG_TEST_FILE,
           '-a', QIF_TEST_FILE])
    @patch('qifqif.quick_input',
           side_effect=['Y'] + KEYBOARD_INPUTS + [EOFError])
    def test_revert_on_eof(self, mock_quick_input):
        """Check that config and dest files are not edited when exiting on EOF.
        """
        res = qifqif.main()
        self.assertEqual(get_data(QIF_FILE), get_data(QIF_TEST_FILE))
        self.assertEqual(get_data(CONFIG_FILE), get_data(CONFIG_TEST_FILE))
        self.assertEqual(res, 1)

    @patch('qifqif.quick_input',
           side_effect=KEYBOARD_INPUTS + [KeyboardInterrupt])
    def test_sigint(self, mock_quick_input):
        """Check that processed transactions are not lost on interruption.
        """
        res = qifqif.process_file(self.transactions, {'config': CONFIG_FILE,
                                  'audit': True, 'dry-run': True})
        self.assertEqual(res[1]['category'], 'Drink')

    @patch('sys.argv', ['qifqif', '-c', CONFIG_TEST_FILE,
           '-a', QIF_TEST_FILE])
    @patch('qifqif.quick_input',
           side_effect=['Y'] + KEYBOARD_INPUTS + [KeyboardInterrupt])
    def test_save_on_sigint(self, mock_quick_input):
        """Check that dest file has all transactions and has been edited.
        """
        res = qifqif.main()
        self.assertNotEqual(get_data(QIF_FILE), get_data(QIF_TEST_FILE))
        self.assertNotEqual(get_data(CONFIG_FILE), get_data(CONFIG_TEST_FILE))
        self.assertEqual(res, 1)
        self.assertEqual(len(qifqif.parse_file(
                         get_data(QIF_TEST_FILE, as_lines=True),
                         {'batch': True})), 3)

if __name__ == '__main__':
    unittest.main()

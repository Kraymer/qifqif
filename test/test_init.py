#!/usr/bin/env python

"""Units tests for __init__.py"""

import unittest

from mock import patch

import qifqif
from qifqif import qifile
import testdata

OPTIONS = qifqif.parse_args(['qifqif', '-d', '-c', testdata.CFG_FILE, 'dummy'])


def mock_input_default(prompt, choices='', vanish=False):
    """Enter default choice at prompts
    """
    res = [x for x in choices if x.isupper()]
    return res[0] if res else ''


class TestInit(unittest.TestCase):
    @patch('__builtin__.raw_input', return_value='')
    def test_quick_input(self, mock_raw_input):
        self.assertEqual(qifqif.quick_input('', 'Yn'), 'Y')
        self.assertEqual(qifqif.quick_input('', ('no', 'Yes', 'maybe')), 'Yes')

    def test_parse_default_transaction(self):
        res = qifile.parse_lines(testdata.generate_lines('PDM'))
        self.assertEqual(len(res), 1)

    def test_parse_delimiter_optional(self):
        res_no_delim = qifile.parse_lines(testdata.generate_lines('PDM^P'))
        res_delim_end = qifile.parse_lines(testdata.generate_lines('PDM^P^'))
        res_delim_ends = qifile.parse_lines(testdata.generate_lines('^PDM^P^'))
        self.assertEqual(res_no_delim, res_delim_end)
        self.assertEqual(res_delim_end, res_delim_ends)

    def test_parse_empty_transaction(self):
        res = qifile.parse_lines(testdata.generate_lines('PDM^^'))
        self.assertEqual(len(res), 1)

    def test_dump_to_buffer(self):
        transactions, lines = testdata.transactions()
        res = qifile.dump_to_buffer(transactions)
        self.assertEqual(res, ''.join(lines))


class TestInitWithConfig(unittest.TestCase):
    def setUp(self):
        qifqif.tags.load(testdata.CFG_FILE)

    @patch('qifqif.quick_input', side_effect=mock_input_default)
    def test_audit_mode_no_edit(self, mock_quick_input):
        OPTIONS['audit'] = True
        res = qifqif.process_transactions(testdata.transactions()[0], OPTIONS)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['category'], 'Bars')

    @patch('sys.argv', ['qifqif', '-c', testdata.CFG_FILE, '-b', '-d',
           testdata.QIF_FILE])
    def test_main(self):
        res = qifqif.main()
        self.assertEqual(res, 0)

if __name__ == '__main__':
    unittest.main()

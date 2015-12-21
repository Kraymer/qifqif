#!/usr/bin/env python

"""Units tests for __init__.py"""

import os
import io
import unittest

import qifqif
from testdata import generate_lines

QIF_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', 'transac.qif')


class TestInit(unittest.TestCase):
    def test_parse_args(self):
        self.assertFalse(qifqif.parse_args(['qifqif', '-a', '-b', 'in.qif']))
        args = qifqif.parse_args(['qifqif', 'file.qif'])
        self.assertEqual(args['dest'], args['src'])

    def test_parse_default_transaction(self):
        res = qifqif.parse_lines(generate_lines('PDM'))
        self.assertEqual(len(res), 1)

    def test_parse_delimiter_optional(self):
        res_no_delim = qifqif.parse_lines(generate_lines('PDM^P'))
        res_delim_end = qifqif.parse_lines(generate_lines('PDM^P^'))
        res_delim_ends = qifqif.parse_lines(generate_lines('^PDM^P^'))
        self.assertEqual(res_no_delim, res_delim_end)
        self.assertEqual(res_delim_end, res_delim_ends)

    def test_parse_empty_transaction(self):
        res = qifqif.parse_lines(generate_lines('PDM^^'))
        self.assertEqual(len(res), 1)

    def test_dump_to_buffer(self):
        with io.open(QIF_FILE, 'r', encoding='utf-8') as fin:
            lines = fin.readlines()
            transactions = qifqif.parse_lines(lines)
        res = qifqif.dump_to_buffer(transactions)
        self.assertEqual(res, ''.join(lines))


if __name__ == '__main__':
    unittest.main()

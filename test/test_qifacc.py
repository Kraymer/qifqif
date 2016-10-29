#!/usr/bin/env python

"""Units tests for qifacc.py"""

import os
import unittest

from qifqif import qifacc
import testdata

OPTIONS = {'dry-run': True, 'config': testdata.CFG_FILE}
RSRC = os.path.join(os.path.realpath(os.path.dirname(__file__)), 'rsrc')
CFG_FILE = os.path.join(RSRC, 'config.json')
CSV_FILE = os.path.join(RSRC, 'accounts.csv')


class TestQifacc(unittest.TestCase):

    def test_read_accounts(self):
        res = qifacc.read_accounts(CSV_FILE, 2)
        self.assertEqual(res, ['MYBANK', 'Bars'])

    def test_write_config(self):
        res = qifacc.write_config(['MYBANK', 'Bars'], CFG_FILE, dry_run=True)
        self.assertEqual(res['MYBANK'], [])
        self.assertNotEqual(res['Bars'], [])
        self.assertTrue(len(res.keys()) > 2)


if __name__ == '__main__':
    unittest.main()

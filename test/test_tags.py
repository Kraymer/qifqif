#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Units tests"""

import unittest
import copy

from qifqif import tags
from testdata import TAGS, TRANSACTION

OPTIONS = {'dry-run': True}


class TestPayeeTransaction2(unittest.TestCase):
    def setUp(self):
        tags.TAGS = copy.deepcopy(TAGS)

    def test_find_tag_for_basic_ruler(self):
        tag, ruler = tags.find_tag_for({'payee': 'SuLLy'})
        self.assertEqual(tag, 'Bars')
        tag, ruler = tags.find_tag_for({'payee': 'Sullyz Sull'})
        self.assertEqual(tag, None)

    def test_find_tag_for_best_ruler(self):
        tag, ruler = tags.find_tag_for({'payee': 'Foo Art Brut Shop'})
        self.assertEqual(tag, 'Clothes')

    def test_basic_ruler_insensitive_case(self):
        self.assertTrue(tags.match('sully bar', TRANSACTION))

    def test_basic_ruler_no_partial_match(self):
        self.assertTrue(tags.match('sully ba', TRANSACTION))

    def test_edit(self):
        res = tags.edit(TRANSACTION, 'Drinks', 'Sully bar', OPTIONS)
        self.assertEqual(set(res.keys()), set(['Bars', 'Clothes', 'Drinks']))
        self.assertEqual(res['Bars'], ['Art Brut'])

    def test_edit_drop_empty_category(self):
        t = TRANSACTION.copy()
        t['payee'] = 'FOO Art Brut Shop BAR'
        res = tags.edit(t, 'SPAM', 'FOO', OPTIONS)
        self.assertEqual(set(res.keys()), set(['Bars', 'SPAM']))


if __name__ == '__main__':
    unittest.main()

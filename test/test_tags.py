#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Units tests"""

import unittest
import copy

from qifqif import tags
from testdata import TAGS, TRANSACTION

OPTIONS = {'dry-run': True}


class TestTags(unittest.TestCase):
    def setUp(self):
        tags.TAGS = copy.deepcopy(TAGS)

    def test_rulify(self):
        self.assertEqual(tags.rulify('alice'), {'PAYEE': r'\balice\b'})
        d = {'memo': 'alice'}
        self.assertEqual(tags.rulify(d), d)

    def test_unrulify__basic_ruler(self):
        self.assertEqual(tags.unrulify({'PAYEE': r'\balice\b'}), 'alice')

    def test_unrulify__noop(self):
        for d in ({'payee': r'\balice\b'}, 'alice'):
            self.assertEqual(tags.unrulify(d), d)

    def test_match__basic_ruler_insensitive_case(self):
        self.assertTrue(tags.match('sully bar', TRANSACTION))

    def test_match__ruler_no_partial_match(self):
        self.assertTrue(tags.match('sully ba', TRANSACTION))

    def test_find_tag_for__basic_ruler(self):
        tag, ruler, _ = tags.find_tag_for({'payee': 'SuLLy'})
        self.assertEqual(tag, 'Bars')
        tag, ruler, _ = tags.find_tag_for({'payee': 'Sullyz Sull'})
        self.assertEqual(tag, None)

    def test_find_tag_for__best_ruler(self):
        tag, ruler, _ = tags.find_tag_for({'payee': 'Foo Art Brut Shop'})
        self.assertEqual(tag, 'Clothes')

    def test_convert(self):
        res = tags.convert({'foo': ['bar', {'memo': 'rabbit'}],
                'bacon': ['spam']})
        self.assertEqual(res,
            {'foo': [{'PAYEE': r'\bbar\b'},
                    {'memo': 'rabbit'}],
                'bacon': [{'PAYEE': r'\bspam\b'}]})

    def test_edit(self):
        res = tags.edit(TRANSACTION, 'Drinks', 'Sully bar', OPTIONS)
        self.assertEqual(set(res.keys()), set(['Bars', 'Clothes', 'Drinks']))
        self.assertEqual(res['Bars'], ['Art Brut'])
        res = tags.edit(TRANSACTION, 'Drinks', {'payee': 'Sully'}, OPTIONS)
        self.assertEqual(res['Drinks'], [{'payee': 'Sully'}])

    def test_edit__drop_empty_category(self):
        t = TRANSACTION.copy()
        t['payee'] = 'FOO Art Brut Shop BAR'
        res = tags.edit(t, 'SPAM', 'FOO', OPTIONS)
        self.assertEqual(set(res.keys()), set(['Bars', 'SPAM']))


if __name__ == '__main__':
    unittest.main()

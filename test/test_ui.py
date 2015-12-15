#!/usr/bin/env python

"""Units tests for ui.py"""

import unittest

from qifqif import ui


class TestUi(unittest.TestCase):
    def test_completer(self):
        self.assertEqual(set(ui.complete_matches('A: B,C')), set(['A',
                         'A: B,C', 'B', 'B,C', 'C']))


if __name__ == '__main__':
    unittest.main()

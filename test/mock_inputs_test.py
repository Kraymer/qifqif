import unittest
import tempfile
import io

from mock import patch

import qifqif
from qifqif import qifile
import testdata

OUT_FILE = tempfile.NamedTemporaryFile()
OPTIONS = qifqif.parse_args(['qifqif', '-d', '-c', testdata.CFG_FILE, 'dummy'])


KEYBOARD_BASE = [
    'Y',      # Edit 'Bars' category [y,N] ?
    'Drink',  # Category
]


class TestBlackBox(unittest.TestCase):
    def setUp(self):
        qifqif.tags.load(testdata.CFG_FILE)

    KEYBOARD_INPUTS = [
        'memo',  # match on field
        'houf',  # memo match (chars)
        'date*',  # match on field
        '\d\d/02/2014',  # date match (regex)
        ''  # match on field
    ]

    @patch('sys.argv', ['qifqif', '-c', testdata.CFG_FILE, '-a',
           testdata.QIF_FILE])
    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_query_guru_ruler(self, mock_quick_input):
        t, _ = testdata.transactions()
        res = qifqif.query_guru_ruler(t[0])
        self.assertEqual(res, {u'date': r'\d\d/02/2014', u'memo': 'houf'})

    KEYBOARD_INPUTS = KEYBOARD_BASE + [
        'Sally',  # Bad payee match
        'Sully',  # Payee match
        '',       # Edit 'Restaurant' category [y,N] ?
        '']       # Press any key

    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_audit_mode(self, mock_quick_input):
        OPTIONS['audit'] = True
        res = qifqif.process_transactions(testdata.transactions()[0], OPTIONS)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['category'], 'Drink')

    KEYBOARD_INPUTS = KEYBOARD_BASE + [
        EOFError]  # Ctrl+D

    @patch('sys.argv', ['qifqif', '-c', testdata.CFG_FILE, '-a',
           testdata.QIF_FILE])
    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_revert_on_eof(self, mock_quick_input):
        """Check that config and dest files are not edited when exiting on EOF.
        """
        qif_original = open(testdata.QIF_FILE, 'rb').read()
        cfg_original = open(testdata.CFG_FILE, 'rb').read()
        res = qifqif.main()
        self.assertEqual(qif_original, open(testdata.QIF_FILE, 'rb').read())
        self.assertEqual(cfg_original, open(testdata.CFG_FILE, 'rb').read())
        self.assertEqual(res, 1)

    KEYBOARD_INPUTS = KEYBOARD_BASE + [
        KeyboardInterrupt]  # Ctrl+D

    @patch('sys.argv', ['qifqif', '-c', testdata.CFG_FILE, '-a',
           testdata.QIF_FILE, '-o',
           OUT_FILE.name])
    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_sigint(self, mock_quick_input):
        """Check that processed transactions are not lost on interruption.
        """
        qifqif.main()
        with io.open(OUT_FILE.name, 'r', encoding='utf-8') as fin:
            res = qifile.parse_lines(fin.readlines())
        self.assertEqual(res[0]['category'], 'Drink')


if __name__ == '__main__':
    unittest.main()

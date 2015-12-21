import io
import os
import unittest
import tempfile

from mock import patch

import qifqif

CFG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    'rsrc', 'config.json')
QIF_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', 'transac.qif')
OUT_FILE = tempfile.NamedTemporaryFile()

OPTIONS = {'dry-run': True, 'config': CFG_FILE}

KEYBOARD_BASE = [
    'Y',      # Edit 'Bars' category [y,N] ?
    'Drink',  # Category
]


def mock_input_default(prompt, choices='', vanish=False):
    """Enter default choice at prompts
    """
    res = [x for x in choices if x.isupper()]
    return res[0] if res else ''


class TestBlackBox(unittest.TestCase):
    def setUp(self):
        qifqif.tags.load(CFG_FILE)
        with io.open(QIF_FILE, 'r', encoding='utf-8') as fin:
            self.transactions = qifqif.parse_lines(fin.readlines())

    @patch('qifqif.quick_input', side_effect=mock_input_default)
    def test_audit_mode_no_edit(self, mock_quick_input):
        OPTIONS['audit'] = True
        res = qifqif.process_file(self.transactions, OPTIONS)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['category'], 'Bars')

    KEYBOARD_INPUTS = KEYBOARD_BASE + [
        'Sully',  # Payee match
        '',       # Edit 'Restaurant' category [y,N] ?
        '']       # Press any key

    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_audit_mode(self, mock_quick_input):
        OPTIONS['audit'] = True
        res = qifqif.process_file(self.transactions, OPTIONS)
        self.assertEqual(len(res), 2)
        self.assertEqual(res[0]['category'], 'Drink')

    @patch('sys.argv', ['qifqif', '-c', CFG_FILE, '-b', '-d', QIF_FILE])
    def test_main(self):
        res = qifqif.main()
        self.assertEqual(res, 0)

    KEYBOARD_INPUTS = KEYBOARD_BASE + [
        EOFError]  # Ctrl+D

    @patch('sys.argv', ['qifqif', '-c', CFG_FILE, '-a', QIF_FILE])
    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_revert_on_eof(self, mock_quick_input):
        """Check that config and dest files are not edited when exiting on EOF.
        """
        qif_original = open(QIF_FILE, 'rb').read()
        cfg_original = open(CFG_FILE, 'rb').read()
        res = qifqif.main()
        self.assertEqual(qif_original, open(QIF_FILE, 'rb').read())
        self.assertEqual(cfg_original, open(CFG_FILE, 'rb').read())
        self.assertEqual(res, 1)

    KEYBOARD_INPUTS = KEYBOARD_BASE + [
        KeyboardInterrupt]  # Ctrl+D

    @patch('sys.argv', ['qifqif', '-c', CFG_FILE, '-a', QIF_FILE, '-o',
           OUT_FILE.name])
    @patch('qifqif.quick_input', side_effect=KEYBOARD_INPUTS)
    def test_sigint(self, mock_quick_input):
        """Check that processed transactions are not lost on interruption.
        """
        qifqif.main()
        with io.open(OUT_FILE.name, 'r', encoding='utf-8') as fin:
            res = qifqif.parse_lines(fin.readlines())
        self.assertEqual(res[0]['category'], 'Drink')


if __name__ == '__main__':
    unittest.main()

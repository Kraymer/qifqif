#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import readline

from clint.textui import colored
from difflib import SequenceMatcher

from qifqif import tags


readline.parse_and_bind('tab: complete')

# Flag that tracks if last ink() print statement on stdout is turning
# invisible (hence 'magic ink' linguo) or not.
MAGIC_INK_DRYING = False


def ink(text, magic=False):
    """ Wrap every string you print in an ink() call to enable magic ink
        feature aka *print that turns invisible*.
        Note: Use ANSI terminal codes, not supported on Windows

        If magic is True, text will be overwritten by next ink() print.
        If magic is False, text is printed permanently (like any other
        print-like call).
        If the previous ink call was magic, then ANSI code is prepended to text
        so as to overwrite previous terminal line.
    """
    global MAGIC_INK_DRYING

    def overwrite(text=''):
        return '\x1b[1A\x1b[1M' + text

    res = text
    if MAGIC_INK_DRYING:
        res = overwrite(text)
    MAGIC_INK_DRYING = magic
    return res


def diff(a, b, as_error=False):
    """ Return a string representing how well b matches a string : matching
        words are green, partial matches (chars) are orange.
        If as_error is True, non matching chars are red.
    """

    s = SequenceMatcher(None, a.lower(), b.lower())
    match_indexes = s.find_longest_match(0, len(a), 0, len(b))
    _, x, y = match_indexes
    match = b[x:x + y]
    words = match.split(' ')
    res = colored.red(b[:x]) if as_error else b[:x]
    for w in words:
        res += (colored.green(w) if tags.is_match(w, a)
                else colored.yellow(w)) + ' '
    res += '\b' + (colored.red(b[x + y:]) if as_error else b[x + y:])
    return res


class InputCompleter(object):
    def __init__(self, options):
        self.options = options

    def complete(self, text, state):
        readline.redisplay()
        if state == 0:
            if text:
                self.matches = [s for s in self.options
                                if s and s.startswith(text)]
            else:
                self.matches = self.options[:]
        try:
            return self.matches[state]
        except IndexError:
            return None


def set_completer(options=None):
    if options:
        completer = InputCompleter(options)
        readline.set_completer(completer.complete)
    else:
        readline.set_completer(None)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import readline

from difflib import SequenceMatcher

from qifqif import tags


readline.parse_and_bind('tab: complete')


def diff(a, b, term, as_error=False):
    """ Return a string representing how well b matches a string : matching
        words are green, partial matches (chars) are orange.
        If as_error is True, non matching chars are red.
    """

    s = SequenceMatcher(None, a.lower(), b.lower())
    match_indexes = s.find_longest_match(0, len(a), 0, len(b))
    _, x, y = match_indexes
    match = b[x:x + y]
    words = match.split(' ')
    res = term.red(b[:x]) if as_error else b[:x]
    for w in words:
        res += (term.green(w) if tags.is_match(w, a)
                else term.yellow(w)) + ' '
    res += '\b' + (term.red(b[x + y:]) if as_error else b[x + y:])
    return res


class InputCompleter(object):
    def __init__(self, options):
        self.options = options

    def complete(self, text, state):
        readline.redisplay()
        if state == 0:
            if text:
                self.matches = [s for s in self.options
                                if s and s.lower().startswith(text.lower())]
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

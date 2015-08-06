#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Utilities functions related to terminal display"""

import readline
import re

from difflib import SequenceMatcher

from qifqif import tags


readline.parse_and_bind('tab: complete')


def diff(_str, candidate, term, as_error=False):
    """ Return a string representing how well candidate matches str : matching
        words are green, partial matches (chars) are orange.
        If as_error is True, non matching chars are red.
    """

    match = SequenceMatcher(None, _str.lower(), candidate.lower())
    match_indexes = match.find_longest_match(0, len(_str), 0, len(candidate))
    _, beg, end = match_indexes
    match = candidate[beg:beg + end]
    words = match.split(' ')
    res = term.red(candidate[:beg]) if as_error else candidate[:beg]
    for w in words:
        res += (term.green(w) if tags.is_match(w, _str)
                else term.yellow(w)) + ' '
    res += '\b' + (term.red(candidate[beg + end:]) if as_error
                   else candidate[beg + end:])
    return res


class InputCompleter(object):
    """Input completer for categories"""

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
        readline.set_completer_delims('')
    else:
        readline.set_completer(None)


def complete_matches(payee):
    """Generate a limited set of matches for payee line"""

    matches = [m for m in re.findall(r"\w+", payee) if m]
    select = True
    for (i, c) in enumerate(payee):
        if c.isalnum() and select:
            matches.append(payee[i:])
        select = not c.isalnum()
    return matches

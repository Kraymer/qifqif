#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Utilities functions related to terminal display"""

import readline
import re

from difflib import SequenceMatcher


readline.parse_and_bind('tab: complete')


def sub_re(pattern):
    for offset in range(len(pattern) + 1, 0, -1):
        try:
            re_obj = re.compile(pattern[:offset])
        except re.error:  # syntax error in re part
            continue
        yield offset, re_obj


def partial_pattern_match(pattern, text):
    print('%s/%s' % (pattern, text))
    good_pattern_offset = 0
    good_text_offset = 0
    for re_offset, re_obj in sub_re(pattern):
        print('match %s?' % text)
        match = re_obj.search(text)
        if match:
            good_pattern_offset = re_offset
            good_text_offset = match.start()
            return good_pattern_offset, good_text_offset
    return good_pattern_offset, good_text_offset


def diff(_str, candidate, term, as_error=False):
    match = SequenceMatcher(None, _str.lower(), candidate.lower())
    match_indexes = match.find_longest_match(0, len(_str), 0, len(candidate))
    _, beg, end = match_indexes
    match = candidate[beg:beg + end]
    words = match.split(' ')
    res = term.red(candidate[:beg]) if as_error else candidate[:beg]
    for w in words:
        res += (term.green(w) if re.search(r'\b%s\b' % re.escape(w), _str, re.I)
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

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Utilities functions related to terminal display."""

import re
from difflib import SequenceMatcher
from itertools import chain, combinations

from qifqif.terminal import TERM


def colorize_match(t, field, matches=None):
    field_val = t[field]
    if not field_val:
        return None
    match = matches.get(field, '') if matches else ''
    seqmatch = SequenceMatcher(None, field_val, match)
    a, b, size = seqmatch.find_longest_match(0, len(field_val), 0, len(match))
    return (field_val[:a] + TERM.green(field_val[a:a + size]) +
            field_val[a + size:])


def complete_matches(payee):
    """Generate a limited set of matches for payee line.

    >>> complete_matches("foo bar spam")
    ['foo', 'bar', 'spam', 'foo bar spam', 'bar spam', 'spam']
    """
    matches = []
    tokens = payee.split()
    sublists = chain(*(combinations(tokens, i) for i in range(len(tokens) + 1)))
    for x in sublists:
        match = " ".join(x)
        if match and (match in payee):
            matches.append(match)
    return matches

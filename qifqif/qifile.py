#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

try:
    from collections import OrderedDict
except ImportError:  # python 2.6
    from ordereddict import OrderedDict

from qifqif import config


def parse_lines(lines, options=None):
    """Return list of transactions as ordered dicts with fields save in same
       order as they appear in input file.
    """
    if not options:
        options = {}
    res = []
    transaction = OrderedDict()
    for (idx, line) in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        field_id = line[0]
        if field_id == '^':
            if transaction:
                res.append(transaction)
            transaction = OrderedDict([])
        elif field_id in list(config.FIELDS.keys()):
            transaction[config.FIELDS[field_id]] = line[1:]
        elif line:
            transaction['%s' % idx] = line

    if len(list(transaction.keys())):
        res.append(transaction)

    # post-check to not interfere with present keys order
    for t in res:
        for field in list(config.FIELDS.values()):
            if field not in t:
                t[field] = None
        t[u'filename'] = options.get('src', '')
    return res


def dump_to_buffer(transactions):
    """Output transactions to file or terminal.
    """
    reverse_fields = {}
    for (key, val) in list(config.FIELDS.items()):
        reverse_fields[val] = key
    lines = []
    for t in transactions:
        for key in t:
            if t[key] and key not in list(config.EXTRA_FIELDS.values()):
                try:
                    lines.append('%s%s\n' % (reverse_fields[key], t[key]))
                except KeyError:  # Unrecognized field
                    lines.append(t[key] + '\n')
        lines.append('^\n')
    res = ''.join(lines).strip() + '\n'
    return res

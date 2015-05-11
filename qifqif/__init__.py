#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import os
import sys
from clint.textui import puts, colored
from collections import OrderedDict

from qifqif import tags

from qifqif.ui import ink, diff, set_completer


def query_tag(cached_cat):
    set_completer(sorted(tags.TAGS.keys()))
    tag = raw_input(ink('Category: ', magic=True))
    if not tag and cached_cat:
        erase = raw_input(ink("Remove existing tag [y,N]? ",
                          magic=True)) or 'N'
        if erase.upper() == 'N':
            tag = cached_cat
    set_completer()
    return tag


def query_match(cached_match, payee):
    while True:
        match = raw_input(ink("Match: ", magic=True))
        if not tags.is_match(match, payee):
            puts(ink('%s Match rejected: %s') %
                 (colored.red('✖'), diff(payee, match, as_error=True)))
        else:
            puts(ink("%s Match accepted: %s" % (colored.green('✔'),
                 str(match) if match else colored.red('<none>'))))
            break
    return match


def process_transaction(amount, payee, cached_tag, cached_match, options):
    puts(ink('Amount..: %s' % (colored.green(amount) if float(amount) > 0
         else colored.red(amount))))
    puts(ink('Payee...: %s' % (diff(cached_match, payee) if cached_match
         else payee)))
    tag, match = cached_tag, cached_match
    edit = False
    if cached_tag:
        if options['audit']:
            msg = ink("Edit '%s' category [y/N]? " % colored.green(cached_tag),
                      magic=True)
            edit = (raw_input(msg) or 'N').lower() == 'y'
    if not cached_tag or edit:
        tag = query_tag(cached_tag)
    puts(ink('Category: %s') % (colored.green(tag) if tag else
         colored.red('<none>')))
    if tag and (not cached_match or edit):
        match = query_match(cached_match, payee)
    return tag or cached_tag, match


def process_file(transactions, options):
    tag = None

    for t in transactions:
        if 'payee' in t:
            cached_tag, cached_match = tags.find_tag_for(t['payee'])
            if not options['batch']:
                tag, match = process_transaction(t['amount'], t['payee'],
                                                 cached_tag, cached_match,
                                                 options)
            else:
                tag, match = cached_tag, cached_match
            tags.save(options['config'], cached_tag, cached_match, tag, match)
            t['category'] = tag
        else:
            print('Skip transaction: no payee')
        if not options['batch']:
            separator = '-' * 3
            print ink(separator) if tag else separator
    return transactions


FIELDS = {'D': 'date', 'T': 'amount', 'P': 'payee', 'L': 'category'}


def parse_file(lines):
    """Return list of transactions as ordered dicts with fields save in same
       order as they appear in input file.
    """
    res = []
    transaction = OrderedDict()

    for (idx, line) in enumerate(lines):
        field_id = line[0]
        if field_id == '^':
            res.append(transaction)
            transaction = OrderedDict()
        elif field_id in ('D', 'T', 'P'):
            transaction[FIELDS[field_id]] = line[1:].strip()
        else:
            transaction[idx] = line
    if transaction:
        res.append(transaction)
    return res


def dump_to_file(dest, transactions, options):
    reverse_fields = {v: k for (k, v) in FIELDS.items()}
    lines = []
    for t in transactions:
        for key in t:
            try:
                lines.append('%s%s\n' % (reverse_fields[key], t[key]))
            except KeyError:  # Unrecognized field
                lines.append(t[key])
        lines.append('^\n')
    with open(dest, 'w') as f:
        f.writelines(lines)
    if options['batch']:
        print ''.join(lines).strip()


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = argparse.ArgumentParser(
        description='Enrich your .QIF files with tags. '
        'See https://github.com/Kraymer/qifqif for more infos.')
    parser.add_argument('src', metavar='QIF_FILE',
                        help='.QIF file to process', default='')
    parser.add_argument('-a', '--audit-mode', dest='audit',
                        action='store_true', help=('pause after '
                                                   'each transaction'))
    parser.add_argument('-c', '--config', dest='config',
                        help='configuration filename in json format. '
                        'DEFAULT: ~/.qifqif.json',
                        default=os.path.join(os.path.expanduser('~'),
                                             '.qifqif.json'))
    parser.add_argument('-o', '--output', dest='dest',
                        help='output filename. '
                        'DEFAULT: edit input file in-place', default='')
    parser.add_argument('-b', '--batch-mode', action='store_true',
                        dest='batch', help=('skip transactions that require '
                                            'user input'))

    args = vars(parser.parse_args())
    if not args['dest']:
        args['dest'] = args['src']
    if args['audit'] and args['batch']:
        print 'Error: cannot activate batch-mode when audit-mode is already on'
        exit(1)

    tags.load(args['config'])

    with open(args['src'], 'r') as f:
        lines = f.readlines()

    transactions = parse_file(lines)
    transactions = process_file(transactions, options=args)

    dump_to_file(args['dest'], transactions, options=args)


if __name__ == "__main__":
    sys.exit(main())

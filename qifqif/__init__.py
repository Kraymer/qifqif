#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

from __future__ import (print_function, unicode_literals)

import argparse
import os
import sys
from collections import OrderedDict
from blessed import Terminal

from qifqif import tags

from qifqif.ui import diff, set_completer

term = Terminal()
CLEAR = term.move_up + term.move_x(0) + term.clear_eol


def query_tag(cached_cat):
    set_completer(sorted(tags.TAGS.keys()))
    with term.location():
        tag = raw_input('Category: ')
    if not tag and cached_cat:
        with term.location():
            erase = raw_input("Remove existing tag [y,N]? ") or 'N'
        if erase.upper() == 'N':
            tag = cached_cat
    set_completer()
    return tag


def query_match(cached_match, payee):
    while True:
        with term.location():
            match = raw_input("Match: ")
        if not tags.is_match(match, payee):
            print('%s Match rejected: %s') % \
                (term.red('✖'), diff(payee, match, as_error=True))
        else:
            print("%s Match accepted: %s" %
                  (term.green('✔'), str(match) if match else
                   term.red('<none>')))
            break
    return match


def process_transaction(amount, payee, cached_tag, cached_match, options):
    print('Amount..: %s' % (term.green(str(amount)) if
          (amount and float(amount) > 0) else term.red(str(amount))))
    print('Payee...: %s' % (diff(cached_match, payee) if cached_match
                            else payee))
def query_save():
    choices = [highlight_char(x) for x in
               ('Categories', 'destination', 'both', 'nothing')]
    print(term.move_down * 3 + '(save %s, %s, %s or %s)' %
          tuple(choices), end='')
    print(term.move_up + CLEAR, end='')
    return raw_input('---\nSave [C,d,b,n]? ').upper()
    tag, match = cached_tag, cached_match
    if not options['batch']:
        edit = False
        if cached_tag:
            if options['audit']:
                with term.location():
                    msg = "Edit '%s' category [y/N]? " % term.green(cached_tag)
                    edit = (raw_input(msg) or 'N').lower() == 'y'
        if payee and (not cached_tag or edit):
            tag = query_tag(cached_tag)
        print('Category: %s') % (term.green(tag) if tag
                                 else term.red('<none>'))
        if tag and (not cached_match or edit):
            match = query_match(cached_match, payee)
    return tag or cached_tag, match


def process_file(transactions, options):
    tag = None

    for t in transactions:
        cached_tag, cached_match = tags.find_tag_for(t['payee'])

        tag, match = process_transaction(t['amount'], t['payee'],
                                         cached_tag, cached_match,
                                         options)

        tags.save(options['config'], cached_tag, cached_match, tag, match)
        t['category'] = tag
        if 'payee' not in t:
            print('Skip transaction: no payee')
        if not options['batch']:
            separator = '-' * 3
            print(separator)
    return transactions


FIELDS = {'D': 'date', 'T': 'amount', 'P': 'payee', 'L': 'category',
          'N': 'number'}


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
    # post-check to not interfere with present keys order
    for t in res:
        for field in FIELDS.values():
            if field not in t:
                t[field] = None
    return res


def dump_to_file(dest, transactions, options):
    reverse_fields = {}
    for (k, v) in FIELDS.items():
        reverse_fields[v] = k
    lines = []
    for t in transactions:
        for key in t:
            if t[key]:
                try:
                    lines.append('%s%s\n' % (reverse_fields[key], t[key]))
                except KeyError:  # Unrecognized field
                    lines.append(t[key])
        lines.append('^\n')
    with open(dest, 'w') as f:
        f.writelines(lines[:-1])
    if options['batch']:
        print(''.join(lines).strip())


def highlight_char(word, n=0):
    """Return word with n-th letter highlighted
    """
    return word[:n] + term.reverse(word[n]) + word[n + 1:]


def build_parser():
    """Build application argument parser
    """
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
    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv
    parser = build_parser()

    args = vars(parser.parse_args())
    if not args['dest']:
        args['dest'] = args['src']
    if args['audit'] and args['batch']:
        print(('Error: cannot activate batch-mode when audit-mode is already ',
              'on'))
        exit(1)

    original_tags = tags.load(args['config'])

    with open(args['src'], 'r') as f:
        lines = f.readlines()

    transactions = parse_file(lines)
    save = True
    try:
        transactions = process_file(transactions, options=args)
    except KeyboardInterrupt:
        save = query_save()

    if save is True or save in 'DB':
        dump_to_file(args['dest'], transactions, options=args)
    if save in 'DN':  # restore original tags
        tags.save(args['config'], original_tags)


if __name__ == "__main__":
    sys.exit(main())

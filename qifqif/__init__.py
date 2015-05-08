#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import os
import sys
from clint.textui import puts, colored

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


def print_bad_transaction(lines):
    try:
        idx = list(reversed(lines[:-1])).index('^\n')
    except ValueError:
        idx = -1
    last_transaction = lines[-1 - idx:-1]
    for line in last_transaction:
        if line.startswith('P'):
            break
    else:
        print ''.join(last_transaction)
        puts(colored.red('Error: no payee line defined for transaction'))


def process_file(lines, options):
    result = []
    tag = None
    for line in lines:
        if line.startswith('T'):
            amount = line[1:].strip()
        payee = line[1:].strip() if line.startswith('P') else None
        if payee:  # write payee line and find tag to write on next line
            result.append(line)
            cached_tag, cached_match = tags.find_tag_for(payee)
            if not options['batch']:
                tag, match = process_transaction(amount, payee, cached_tag,
                                                 cached_match, options)
            else:
                tag, match = cached_tag, cached_match

            tags.save(options['config'], cached_tag, cached_match, tag, match)
            result.append('L%s\n' % tag)
        elif line and not line.startswith('L'):  # overwrite previous tags
            result.append(line)
        if line.startswith('^'):
            delimiter = '-' * 3
            print_bad_transaction(result)
            if not options['batch']:
                print ink(delimiter) if tag else delimiter
    if options['batch']:
        print ''.join(result).strip()
    return result


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
        result = process_file(lines, options=args)
    with open(args['dest'], 'w') as f:
        f.writelines(result)


if __name__ == "__main__":
    sys.exit(main())

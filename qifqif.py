#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import json
import os
import re
import readline
import sys

from clint.textui import puts, colored
from difflib import SequenceMatcher


class InputCompleter(object):  # Custom completer
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


def find_tag(tags, payee):
    for (tag, keywords) in tags.items():
        for k in keywords:
            if is_match(k, payee):
                return tag, k
    return None, None


def overwrite(text=''):
    return '\x1b[1A\x1b[1M' + text


def diff(a, b, as_error=False):
    s = SequenceMatcher(None, a.lower(), b.lower())
    match_indexes = s.find_longest_match(0, len(a), 0, len(b))
    _, x, y = match_indexes
    match = b[x:x + y]
    words = match.split(' ')
    res = colored.red(b[:x]) if as_error else b[:x]
    for w in words:
        res += (colored.green(w) if is_match(w, a)
                else colored.yellow(w)) + ' '
    res += '\b' + (colored.red(b[x + y:]) if as_error else b[x + y:])
    return res


def pick_tag(edit, cached_cat, tags):
    completer = InputCompleter(sorted(tags.keys()))
    readline.set_completer(completer.complete)
    tag = raw_input(overwrite('Category: '))
    if not tag and cached_cat:
        erase = raw_input(overwrite("Remove existing tag [y,N]? ")) or 'N'
        if erase.upper() == 'N':
            tag = cached_cat
    readline.set_completer(None)
    return tag


def is_match(match, payee):
    return re.search(r'\b%s\b' % match, payee, re.I) is not None


def pick_match(cached_match, payee):
    while True:
        match = raw_input(overwrite("Match: "))
        if not is_match(match, payee):
            puts(overwrite('%s Match rejected: %s\n') %
                 (colored.red('✖'), diff(payee, match, as_error=True)))
        else:
            puts(overwrite("%s Match accepted: %s\n" % (colored.green('✔'),
                 str(match) if match else colored.red('<none>'))))
            break
    return match


def update_config(cached_tag, cached_match, tag, match, options):
    with open(options['config'], 'r') as cfg:
        tags_saved = json.load(cfg)

    tags = tags_saved.copy()
    if tag and tag != cached_tag:
        if cached_tag:
            tags[cached_tag].remove(cached_match)
            if not tags[cached_tag]:
                del tags[cached_tag]
        if tag and match:
            if tag not in tags:
                tags[tag] = [match]
            else:
                tags[tag].append(match)
    elif match and match != cached_match:
        tags[tag].remove(cached_match)
        tags[tag].append(match)
    else:  # no diff
        return

    with open(options['config'], 'w+') as cfg:
        cfg.write(json.dumps(tags,
                  sort_keys=True, indent=4, separators=(',', ': ')))


def query_tag(amount, payee, cached_tag, cached_match, options):
    puts('Amount..: %s' % (colored.green(amount) if float(amount) > 0
         else colored.red(amount)))
    puts('Payee...: %s\n' % (diff(cached_match, payee) if cached_match
         else payee))
    tag, match = cached_tag, cached_match
    edit = False
    if cached_tag:
        if options['audit']:
            edit = (raw_input(overwrite("Edit '%s' category [y/N]? ") %
                    colored.green(cached_tag)) or 'N').lower() == 'y'
    if not cached_tag or edit:
        tag = pick_tag(cached_tag, options['tags'])
    puts(overwrite('Category: %s') % (colored.green(tag) + '\n' if tag else
         colored.red('<none>')))
    if tag and (not cached_match or edit):
        match = pick_match(cached_match, payee)
    return tag or cached_tag, match


def process_file(lines, options):
    result = []
    for line in lines:
        if line.startswith('T'):
            amount = line[1:].strip()
        payee = line[1:].strip() if line.startswith('P') else None
        if payee:  # write payee line and find tag to write on next line
            result.append(line)
            cached_tag, cached_match = find_tag(options['tags'], payee)
            if not options['batch']:
                tag, match = query_tag(amount, payee, cached_tag, cached_match,
                                       options)
            else:
                tag, match = cached_tag, cached_match

            update_config(cached_tag, cached_match, tag, match, options)
            result.append('L%s\n' % tag)
        elif line and not line.startswith('L'):  # overwrite previous tags
            result.append(line)
        if line.startswith('^'):
            delimiter = '-' * 3
            if not options['batch']:
                print overwrite(delimiter) if tag else delimiter
    if options['batch']:
        print ''.join(result).strip()
    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv
    readline.parse_and_bind('tab: complete')
    parser = argparse.ArgumentParser(
        description='Enrich your .QIF files with tags. '
        'See https://github.com/Kraymer/qifqif for more infos.')
    parser.add_argument('src', metavar='QIF_FILE',
                        help='.QIF file to process', default='')
    parser.add_argument('-a', '--audit-mode', dest='audit',
                        action='store_true', help=('pause after'
                                                   'each transaction'))
    parser.add_argument('-c', '--config', dest='config',
                        help='Configuration filename in json format. '
                        'DEFAULT: ~/.qifqif.json',
                        default=os.path.join(os.path.expanduser('~'),
                                             '.qifqif.json'))
    parser.add_argument('-o', '--output', dest='dest',
                        help='Output filename. '
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

    if os.path.isfile(args['config']):
        with open(args['config'], 'r') as cfg:
            args['tags'] = json.load(cfg)
    else:
        args['tags'] = {}
    with open(args['src'], 'r') as f:
        lines = f.readlines()
        result = process_file(lines, options=args)
    with open(args['dest'], 'w') as f:
        f.writelines(result)


if __name__ == "__main__":
    sys.exit(main())

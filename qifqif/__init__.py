#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import json
import os
import readline
import sys
import re

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


def pick_tag(default_cat, tags):
    completer = InputCompleter(sorted(tags.keys()))
    readline.set_completer(completer.complete)
    tag = raw_input('Category: ')
    if not tag and default_cat:
        erase = raw_input(overwrite("Remove existing tag [y,N]? ")) or 'N'
        if erase.upper() == 'N':
            tag = default_cat
    readline.set_completer(None)
    return tag


def is_match(match, payee):
    return re.search(r'\b%s\b' % match, payee, re.I) is not None


def pick_match(default_match, payee):
    while True:
        match = raw_input(overwrite("Match: "))
        if not is_match(match, payee):
                puts(overwrite('%s Match rejected...: %s\n') %
                     (colored.red('✖'), diff(payee, match, as_error=True)))
        else:
            puts(overwrite("%s Match: %s" % (colored.green('✔'),
                 str(match) if match else colored.red('<none>'))))
            break
    return match


def update_config(cfg_file, prev_tag, prev_match, tag, match, ):
    with open(cfg_file, 'r') as cfg:
        tags_saved = json.load(cfg)

    tags = tags_saved.copy()
    if tag != prev_tag:
        if prev_tag:
            tags[prev_tag].remove(prev_match)
            if not tags[prev_tag]:
                del tags[prev_tag]
        if tag and match:
            if tag not in tags:
                tags[tag] = [match]
            else:
                tags[tag].append(match)
    elif match and match != prev_match:
        tags[tag].remove(prev_match)
        tags[tag].append(match)
    else:  # no diff
        return

    with open(cfg_file, 'w+') as cfg:
        cfg.write(json.dumps(tags,
                  sort_keys=True, indent=4, separators=(',', ': ')))


def fetch_tags(lines, tags, options):
    result = []
    for line in lines:
        if line.startswith('T'):
            amount = line[1:].strip()
        payee = line[1:].strip() if line.startswith('P') else None
        if payee:  # write payee line and find tag to write on next line
            result.append(line)
            prev_tag, prev_match = find_tag(tags, payee)
            tag = prev_tag
            match = prev_match
            puts('Amount..: %s' % (colored.green(amount) if float(amount) > 0
                 else colored.red(amount)))
            puts('Payee...: %s' % (diff(prev_match, payee) if prev_match
                 else payee))
            if prev_tag:
                puts("Category: %s" % prev_tag)
            edit = options['audit']
            if tag and options['audit']:
                edit = (raw_input('Edit [y/N]? ') or 'N').lower() == 'y'
            if not prev_tag or edit:
                tag = pick_tag(prev_tag, tags)
                puts(overwrite('Category: %s') % (tag + '\n' if tag else
                     colored.red('<none>')))
            if tag and (not prev_match or edit):
                match = pick_match(prev_match, payee)
            update_config(options['config'], prev_tag, prev_match, tag, match)
            result.append('L%s\n' % tag)
        elif not line.startswith('L'):  # overwrite previous tags
            result.append(line)
        if line.startswith('^'):
            delimiter = '-' * 3
            print overwrite(delimiter) if (options['audit'] and not edit) \
                else delimiter
    return result, tags


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
    args = vars(parser.parse_args())
    if not args['dest']:
        args['dest'] = args['src']

    if os.path.isfile(args['config']):
        with open(args['config'], 'r') as cfg:
            cfg_dict = json.load(cfg)
    else:
        cfg_dict = {}
    with open(args['src'], 'r') as f:
        lines = f.readlines()
        result, tags = fetch_tags(lines, cfg_dict, options=args)
    with open(args['dest'], 'w') as f:
        f.writelines(result)


if __name__ == "__main__":
    sys.exit(main())

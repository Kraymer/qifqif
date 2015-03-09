#!/usr/bin/env python

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import json
import os
import readline
import sys


def prefilled_input(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return raw_input(prompt)
    finally:
        readline.set_startup_hook()


class InputCompleter(object):  # Custom completer

    def __init__(self, options):
        self.options = sorted(options)

    def complete(self, text, state):
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


def find_category(categories, payee):
    for (c, keywords) in categories.items():
        if any([k.lower() in payee.lower() for k in keywords]):
            return c


def pick_category(payee, categories):
    category = None
    while not category:
        category = raw_input("\nPick a category: ")
        # if not category Skip category [YES, No]
        if category and category not in categories:
            uinput = raw_input('Create new category [YES, Cancel]: ')
            if uinput.upper() not in ['Y', '']:
                category = None
            else:
                categories[category] = []

    save = raw_input('Save association [YES, No]: ')
    if save.upper() in ('Y', ''):
        match = None
        while not match:
            match = prefilled_input('Enter string to match: ', payee)
            if match not in payee:
                print 'match must be a substring of original payee'
                match = None
            categories[category].append(match)
    return (category, categories)


def fetch_categories(lines, categories, options):
    completer = InputCompleter(categories.keys())
    readline.set_completer(completer.complete)
    readline.parse_and_bind('tab: complete')
    result = []
    for line in lines:
        if line.startswith('T'):
            amount = line[1:].strip()
        payee = line[1:].strip() if line.startswith('P') else None
        if payee:  # write payee line and find category to write on next line
            result.append(line)
            category = find_category(categories, payee)
            print amount
            print payee
            while not category:
                category, categories = pick_category(payee, categories)
            print '=> %s' % category
            result.append('L%s\n' % category)
        elif not line.startswith('L'):  # overwrite previous categories
            result.append(line)
        if line.startswith('^'):
            if options['audit']:
                raw_input('Press a key to continue (<ESC> to exit)')
                print('\x1b[1A\x1b[2K---')  # erase last line
            else:
                print '---'
    return result, categories


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Enrich your .QIF files with categories. '
        'See https://github.com/Kraymer/qifhack for more infos.')
    parser.add_argument('src', metavar='QIF_FILE',
                        help='.QIF file to process', default='')
    parser.add_argument('-a', '--audit-mode', dest='audit',
                        action='store_true', help=('pause after'
                                                   'each transaction'))
    parser.add_argument('-o', '--output', dest='dest',
                        help='Output filename. '
                        'DEFAULT: edit input file in-place', default='')
    parser.add_argument('-c', '--config', dest='config',
                        help='Configuration filename in json format. '
                        'DEFAULT: ~/.qifhack.json',
                        default=os.path.join(os.path.expanduser('~'),
                                             '.qifhack.json'))
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
        result, categories = fetch_categories(lines, cfg_dict, options=args)
    with open(args['dest'], 'w') as f:
        f.writelines(result)
    with open(args['config'], 'w+') as cfg:
        cfg.write(json.dumps(categories,
                  sort_keys=True, indent=4, separators=(',', ': ')))

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import json
import os
import readline
import sys

from clint.textui import puts, prompt, colored
from difflib import SequenceMatcher


def read_single_keypress():
    """Waits for a single keypress on stdin.

    This is a silly function to call if you need to do it a lot because it has
    to store stdin's current setup, setup stdin for reading single keystrokes
    then read the single keystroke then revert stdin back after reading the
    keystroke.

    Returns the character of the key that was pressed (zero on
    KeyboardInterrupt which can happen when a signal gets handled)

    """
    import termios, fcntl, sys, os
    fd = sys.stdin.fileno()
    # save old state
    flags_save = fcntl.fcntl(fd, fcntl.F_GETFL)
    attrs_save = termios.tcgetattr(fd)
    # make raw - the way to do this comes from the termios(3) man page.
    attrs = list(attrs_save) # copy the stored version to update
    # iflag
    attrs[0] &= ~(termios.IGNBRK | termios.BRKINT | termios.PARMRK
                  | termios.ISTRIP | termios.INLCR | termios. IGNCR
                  | termios.ICRNL | termios.IXON )
    # oflag
    attrs[1] &= ~termios.OPOST
    # cflag
    attrs[2] &= ~(termios.CSIZE | termios. PARENB)
    attrs[2] |= termios.CS8
    # lflag
    attrs[3] &= ~(termios.ECHONL | termios.ECHO | termios.ICANON
                  | termios.ISIG | termios.IEXTEN)
    termios.tcsetattr(fd, termios.TCSANOW, attrs)
    # turn off non-blocking
    fcntl.fcntl(fd, fcntl.F_SETFL, flags_save & ~os.O_NONBLOCK)
    # read a single keystroke
    try:
        ret = sys.stdin.read(1) # returns a single character
    except KeyboardInterrupt:
        ret = 0
    finally:
        # restore old state
        termios.tcsetattr(fd, termios.TCSAFLUSH, attrs_save)
        fcntl.fcntl(fd, fcntl.F_SETFL, flags_save)
    return ret


def prefilled_input(_prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    readline.redisplay()
    try:
        return raw_input(_prompt) or prefill
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


def overwrite(text):
    return '\x1b[1A\x1b[2K' + text


def diff(a, b):
    s = SequenceMatcher(None, a, b)
    match = s.find_longest_match(0, len(a) - 1, 0, len(b) - 1)
    return '%s%s%s' % (colored.red(b[:match[1]]),
                       colored.green(b[match[1]:match[1] + match[2]]),
                       colored.red(b[match[2]:]))


def pick_category(payee, categories, default_choice=''):
    category = None
    while not category:
        category = prompt.query('Category', default=default_choice)
        # if not category Skip category [YES, No]
        if category.strip() and category not in categories:
            create = prompt.yn(overwrite("Create new '%s' category" %
                               category))
            if not create:
                category = None
            else:
                categories[category] = []

    if category != default_choice:
        match = None
        while True:
            match = prefilled_input('Match...: ', match or payee)
            if match in payee:
                break
            else:
                puts(overwrite('Match...: %s' % diff(payee, match)))
                read_single_keypress()
                print '-> '+match
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
            puts('Amount..: %s' % (colored.green(amount) if float(amount) > 0
                 else colored.red(amount)))
            puts('Payee...: ' + payee)
            prompt = category
            category = '' if options['audit'] else category
            while not category:
                category, categories = pick_category(payee, categories, prompt)
            result.append('L%s\n' % category)
        elif not line.startswith('L'):  # overwrite previous categories
            result.append(line)
        if line.startswith('^'):
            if options['audit']:
                print('Category: %s' % category)  # erase last line
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

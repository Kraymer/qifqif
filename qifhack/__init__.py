#!/usr/bin/env python

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import json
import os
import sys


def find_category(categories, payee):
    for (c, keywords) in categories.items():
        if any([k.lower() in payee.lower() for k in keywords]):
            return c


def fetch_categories(lines, categories):
    result = []
    for line in lines:
        payee = line if line.startswith('P') else None
        if payee:
            result.append(line)
            category = find_category(categories, payee)
            if category:
                result.append('L%s\n' % category)
        else:
            result.append(line)
    return result


def main(argv=None):
    if argv is None:
        argv = sys.argv

    parser = argparse.ArgumentParser(
        description='Enrich your .QIF files with categories. '
        'See https://github.com/Kraymer/qifhack for more infos.')
    parser.add_argument('src', metavar='QIF_FILE',
                        help='.QIF file to process', default='')
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
    with open(args['src'], 'r') as f, open(args['config'], 'r') as cfg:
        cfg_dict = json.load(cfg)
        lines = f.readlines()
        result = fetch_categories(lines, cfg_dict['categories'])
    with open(args['dest'], 'w') as f:
        f.writelines(result)


if __name__ == "__main__":
    sys.exit(main())

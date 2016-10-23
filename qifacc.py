#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import argparse
import csv
import os
import sys

from qifqif import tags

"""Crate categories in qifqif configuration file by importing a csv file
   listing your accounts.
"""


def parse_args(argv):
    """Build application argument parser and parse command line.
    """
    parser = argparse.ArgumentParser(
        description=('Init/update qifqif categories json file by importing '
            'an accounts list in CSV format.'))
    parser.add_argument('-c', '--config', dest='config',
                        help=('configuration filename to update. '
                            'DEFAULT: ~/.qifqif.json'),
                        default=os.path.join(os.path.expanduser('~'),
                                             '.qifqif.json'))
    parser.add_argument('csv', metavar='CSV_FILE',
                        help='.CSV accounts file to process', default='')
    parser.add_argument('-d', '--delimiter', dest='delimiter',
        choices=[',', ';'], default=',', help=('csv delimiter'))
    parser.add_argument('--dry-run', dest='dry_run',
                        action='store_true', help=('dry-run mode: just print '
                            'instead of writing file'))
    parser.add_argument('field', metavar='FIELD',
        type=int, help=('index of field to extract'), default=False)
    args = vars(parser.parse_args(args=argv[1:]))
    return args


def read_accounts(csvfile, field, delimiter=','):
    """Extract accounts from csv file.
    """
    with open(csvfile, 'rb') as csvfile:
        csvrows = csv.reader(csvfile, delimiter=delimiter)
        accounts = [row[field] for row in csvrows]
    return accounts


def write_config(accounts, cfg_path, dry_run):
    """Update configuration file with extracted accounts names.
    """
    json_accs = {}
    for account in accounts:
        json_accs[account] = []
    json_accs.update(tags.load(cfg_path))
    if dry_run:
        print(json_accs)
    else:
        tags.save(cfg_path, json_accs)
    return json_accs


def main(argv=None):
    if argv is None:
        argv = sys.argv
    args = parse_args(argv)
    accounts = read_accounts(args['csv'], args['field'] - 1,
        args['delimiter'])
    write_config(accounts, args['config'], args['dry_run'])


if __name__ == "__main__":
    main()

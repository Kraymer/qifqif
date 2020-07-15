[![][travis]](https://travis-ci.org/Kraymer/qifqif)
[![][coveralls]](https://coveralls.io/r/Kraymer/qifqif)
[![][pypi]](https://pypi.python.org/pypi/qifqif)
[![][rtfd]](http://qifqif.readthedocs.org/en/latest/?badge=latest)
[![][atom]](https://github.com/Kraymer/qifqif/releases.atom)
[![][patreon]](https://www.patreon.com/kraymer)

[travis]: https://travis-ci.org/Kraymer/qifqif.svg?branch=master
[coveralls]: https://coveralls.io/repos/Kraymer/qifqif/badge.svg
[pypi]: http://img.shields.io/pypi/v/qifqif.svg
[rtfd]: https://readthedocs.org/projects/qifqif/badge/?version=latest
[atom]: https://img.shields.io/badge/releases-atom-orange.svg
[patreon]: https://img.shields.io/badge/-%E2%99%A1%20Donate%20-ff69b4

qifqif
======

> **/kĭf kĭf/** :
>   1.  *adj. inv.* arabic slang (كيف) for "it's all the same".
>   2.  *n.* CLI tool for *categorizing* qif files. It can make all the difference.


Description
-----------

CLI tool to *enrich* your QIF files transactions with category
information, hence **cutting down import time from minutes to mere
seconds**.

![](https://raw.githubusercontent.com/Kraymer/qifqif/master/docs/_static/qifqif_demo.gif)

QIF is a format widely used by personal money management software such
as [GnuCash](http://www.gnucash.org/) to import information. Yet, the
import process is particularly tedious as it require to manually pair
the transactions contained in the file with categories (or "accounts"
for double-entry bookkeeping systems).

qifqif augment your qif files by adding a category line for each
transaction, that additional information can then be used by accounting
software to perform automatic QIF imports. It picks categories by
searching for predefined keywords in transactions descriptions lines and
by repeating choices you previously made regarding similar transactions.


Features
--------

- **Quickstart:** create categories by importing your existing accounts with
  [qifacc](https://github.com/Kraymer/qifqif/wiki/qifacc)
- **Blazing fast edits:** thanks to well-thought-out defaults and
  `<TAB>` completion
- **Auditing mode:** review your transactions one by one
- **Batch mode (no interactive):** for easy integration with scripts
- **Easy-going workflow:** dreading the behemoth task of importing
  years of accounting from a single file? Don't be. Go at your own
  pace and press `<Ctrl+C>` to exit anytime. On next run, editing will
  resume right where you left it.

Usage
-----

    usage: qifqif.py [-h] [-a | -b] [-c CONFIG] [-d] [-f] [-o DEST] [-v] QIF_FILE

    Enrich your .QIF files with tags. See https://github.com/Kraymer/qifqif for
    more infos.

    positional arguments:
      QIF_FILE              .QIF file to process

    optional arguments:
      -h, --help            show this help message and exit
      -a, --audit-mode      pause after each transaction
      -b, --batch-mode      skip transactions that require user input
      -c CONFIG, --config CONFIG
                            configuration filename in json format. DEFAULT:
                            ~/.qifqif.json
      -d, --dry-run         just print instead of writing file
      -f, --force           discard transactions categories if not present in
                            configuration file. Repeat the flag (-ff) to force
                            editing of all transactions.
      -o DEST, --output DEST
                            output filename. DEFAULT: edit input file in-place
      -v, --version         display version information and exit

More infos on the [documentation](http://qifqif.rtfd.org) website.

Installation
------------

qiqif is written for [Python 2.7](ttps://www.python.org/downloads/) and
works on Linux and Mac OS X.

Install with [pip](https://pip.pypa.io/en/stable/) via
`pip install qifqif` command.

Changelog
---------

Available on [Github Releases
page](https://github.com/Kraymer/qifqif/releases).

Feedbacks
---------

Please submit bugs and features requests on the [Issue
tracker](https://github.com/Kraymer/qifqif/issues).

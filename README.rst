qifqif
======

CLI tool for quick tagging your QIF files transactions.


Description
-----------

QIF is a format widely used by personal money management software such as
`GnuCash`_ to import information. Yet, the import process is particularly
tedious as it require to manually pair the transactions contained in the file
with categories (or "accounts" for double-entry bookkeeping systems).

qifqif augment your qif files by adding a category line for each transaction,
that additional information can then be used by accounting software to perform
automatic QIF imports.
It picks categories by searching for predefined keywords in transactions
descriptions lines and by repeating choices you previously made regarding
similar transactions.

.. _GnuCash: http://www.gnucash.org/

Features
--------

- **Blazing fast edits:** thanks to well-thought-out defaults and ``<TAB>``
  completion
- **Auditing mode:** review your transactions one by one
- **Quiet mode (no interactive):** for easy integration with scripts
- **Easy-going workflow:** dealing with large files? Press ``<Ctrl+C>`` to exit
  anytime ; on next run, editing will resume right where you left it.


Usage
-----

    usage: qifqif [-h] [-o DEST] [-c CONFIG] QIF_FILE


Installation
------------

    pip install qifqif

Feedbacks
---------

Please submit bugs and features requests on the `Issue tracker`_.

.. _Issue tracker: https://github.com/Kraymer/qifhack/issues

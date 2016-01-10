CLI usage
=========

::

    qifqif.py [-h] [-a | -b] [-c CONFIG] [-d | -o DEST] [-v] QIF_FILE

qifqif inserts a ``L your_category`` line for each transaction
of given QIF_FILE based on your existing matching history stored in CONFIG.

Optional flags:

- ``-a, --audit``: turn it on if you want to inspect every processed transaction
  and category that got applied. Mutually exclusive with ``--batch`` mode as it
  pause the process after each transaction.
- ``-b, --batch``: in this mode, transactions that validate a registered match
  are assigned a category but others are left untouched (no interactive prompt)
- ``-c, --config``: by default, available categories and their matchings are
  saved in ``~/.qifqif.json``. You can choose too to have different config
  files eg one per family member.
- ``-d, --dry-run``: print the result of qifqif work on the standard output
  only, leaving the qif file untouched. Mutually exclusive with ``--output``
- ``-o DEST, --output``: by default input file is edited in-place. Use that
  switch to write in another output file instead.
- ``-v, --version``: display version information and exit

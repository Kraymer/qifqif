Advanced tips
=============

.. |br| raw:: html

   <br />

.. _mastering-keywords:

Mastering keywords
^^^^^^^^^^^^^^^^^^

Two methods of keywords inputs are available. You switch from one to the
other by pressing ``<Enter>`` when presented with a match prompt :

- **payee (full match)** : it's the default method. The keywords must consist
  of successive words present in the payee field.
- **any field (partial match)** : you are first asked to enter a field and then a
  substring to search on this field content. Unlike default full words match,
  the substring is used as-is thus enabling creation of rules based on partial
  word match. Append a ``*`` character when entering the field name to
  unlock the regex input method. |br|
  The two-steps prompt is repeated so you can combine rules on multiple fields.
  Enter no char at prompt to validate the set of rules.


Json configuration file format
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. warning::
   Editing this file manually is not recommended, as any formatting error will make the program exit on error.

.. note::
   qifqif is shipped with `qifacc`_ utility that automates the
   creation of a configuration file from a csv file of exported
   accounts.

.. _qifacc: https://github.com/Kraymer/qifqif/wiki/qifacc

Matchings are saved automatically by qifqif as a json dict.
Keys are the categories, the values are their associated keyword(s).

As an example, here is a valid file defining two categories named *Clothes*
and *Bank accounts* :  ::

    {
        "Clothes": [
            "REEBOOK",
            { "payee": "NIKE", "filename": "BOB"}
        ],
        "Bank accounts": [
            "10203586133",
            { "payee": r"FR\d+"}
        ]
    }

Some comments :

- for the sake of readability, payee keywords -- because they are so common --
  are stored as string. It's just a formatting shortcut, ``REEBOOK`` can be
  written as ``{"payee": "REEBOOK"}`` with no difference whatsoever

- when many keywords expressions match an input transaction, the longer one
  (by number of fields involved and lengthwise) is selected.


Editing/removing existing data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

At match prompt, press twice ``<Enter>`` if you don't want to store a match for
a given transaction.

Enter a match containing only space(s) to undo and go back to edit category
prompt.


Save or discard?
^^^^^^^^^^^^^^^^

Automatic saves allow you to import a large file in multiple runs.
Stop whenever you are bored by pressing ``Ctrl+C`` and resume the task where
you left it at next run.

Use ``Ctrl+D`` to exit brutally and discard all changes


Handling QIF files with no *payee* lines
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default matching method performs search on the payee field
(see :ref:`mastering-keywords`).
The QIF file you process may have this payee information located in another
field like *memo* for example. In such a case it's preferable to pre-process
your file by converting *memo* lines to *payee* lines by switching the line
identifier.
*sed* is a good candidate for that task : ::

    sed -i 's/^M/P/' my_file.qif

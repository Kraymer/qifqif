Getting started
===============

.. |br| raw:: html

   <br />

Install
-------

qiqif is written for `Python 2.7`_ and is tested on Linux, Mac OS X and
(somewhat) Windows.

Install with `pip`_ via ``pip install qifqif`` command.
If you're on Windows and don't have pip yet, follow
`this guide`_ to install it.

To install without pip, download qifqif from `its PyPI page`_ and run ``python
setup.py install`` in the directory therein.

.. _Python 2.7: ttps://www.python.org/downloads/
.. _pip: https://pip.pypa.io/en/stable/
.. _this guide: https://pip.pypa.io/en/latest/installing/
.. _here: https://github.com/Kraymer/qifqif/releases
.. _its PyPI page: http://pypi.python.org/pypi/qifqif#downloads

The best way to upgrade is by running ``pip install -U qifqif``. |br|
A `RSS feed`_ allowing to hear about delivery of new releases is yet to come.

.. _RSS feed: https://github.com/Kraymer/qifqif/issues/40


How it works
------------

qifqif augment your qif files by adding a category line for each transaction,
that additional information can then be used by accounting software to
perform automatic QIF imports.

It picks categories by searching for keywords you previously defined in
transactions fields and by repeating choices you made regarding similar
transactions.

Learning as time goes by
^^^^^^^^^^^^^^^^^^^^^^^^

On first run, qifqif starts with an empty configuration file and prompt you to
enter a category and corresponding keywords for each transaction it reads.

The mappings you enter at prompts are saved in the configuration file which
builds up upon the time as you use the software, allowing qifqif to tag always
more transactions automatically.

.. note::
   While not recommended, it's possible to mass-edit the configuration file in
   a text editor. Typically, the goal would be to add matchings in bulk and
   speed up qifqif learning process as a consequence. |br|
   See explanations about the `configuration file format`_ if you want to go
   that way.

.. _configuration file format: http://qifqif.readthedocs.org/en/latest/tips.html#format-of-the-configuration-file

Entering keywords
^^^^^^^^^^^^^^^^^

The main interaction you will have with qifqif consist to enter a category and
keywords that are required for the transactions to belong to that category.

Entering a category is pretty basic: it can be any string of your choice, use
``<TAB>`` completion to reuse existing ones. |br|
For a software like Gnucash, that info must correspond to the account name you
want the transaction to be attached to.

Entering keywords has a more advanced interface. |br|
Basic & simple case: you enter (successive) word(s) present in the *Payee* field of the current transaction. |br|
If you are interested to detect transactions on field(s) other than *Payee*,
using partial words matching or --foul you!-- using regexes, then please read
`mastering keywords`_.

.. _mastering keywords: http://qifqif.readthedocs.org/en/latest/tips.html#mastering-keywords-prompts


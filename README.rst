qifhack improves your .qif files by inserting additional fields in it from a
pre-configured json mapping file.

I needed it to speed up my .qif imports in `GnuCash`_, but qifhack logic
can be extended to fit others workflows as well (PR welcomed).

One may refer to `Microsoft Money QIF Specification page`_ to have a grasp of
the .qif specification and terminology.

.. _Microsoft Money QIF Specification page: http://money.mvps.org/articles/qifspecification.aspx
.. _GnuCash: http://www.gnucash.org/

Usage
-----

qifhack searches for tokens in each transaction *Payee* field, when a match is
found the token category is applied to the transaction by inserting a
*Category* field.

Tokens must be entered in a json configuration file like so ::

    {
        "categories": {
            "Bars": ["Art Brut", "Indiana", "Sully", "Fontaines", "Hall Beer"],
            "Clothes": ["DPAM", "GAP", "Docker", "Bonobo", "Camper", "Cafe Coton"],
            "Restaurant": ["L'Abri", "Pizza Grill Istanbul"]
        }
    }

Feedbacks
---------

Please submit bugs and features requests on the `Issue tracker`_.

.. _Issue tracker: https://github.com/Kraymer/qifhack/issues

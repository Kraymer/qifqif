#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

FIELDS = {
    "D": u"date",
    "T": u"amount",
    "P": u"payee",
    "L": u"category",
    "N": u"number",
    "M": u"memo",
}
EXTRA_FIELDS = {"F": u"filename"}
FIELDS_FULL = dict(list(FIELDS.items()) + list(EXTRA_FIELDS.items()))

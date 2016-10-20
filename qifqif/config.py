#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

FIELDS = {'D': 'date', 'T': 'amount', 'P': 'payee', 'L': 'category',
          'N': 'number', 'M': 'memo'}
EXTRA_FIELDS = {'F': 'filename'}
FIELDS_FULL = dict(FIELDS.items() + EXTRA_FIELDS.items())

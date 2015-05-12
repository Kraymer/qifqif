#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

import json
import os
import re

TAGS = dict()


def is_match(keyword, payee):
    """Returns True if payee line contains keyword.
    """
    return re.search(r'\b%s\b' % keyword, payee, re.I) is not None


def find_tag_for(payee):
    """If payee contains a saved keyword, returns corresponding tuple
       (tag, keyword).
    """
    global TAGS
    if payee:
        for (tag, keywords) in TAGS.items():
            for k in keywords:
                if is_match(k, payee):
                    return tag, k
    return None, None


def load(filepath):
    """Load tags dictionary.
    """
    global TAGS
    if os.path.isfile(filepath):
        with open(filepath, 'r') as cfg:
            TAGS = json.load(cfg)
    else:
        TAGS = {}


def save(filepath, cached_tag, cached_match, tag, match):
    """Save a tag modification into dictionary and save the latter on file.
    """
    global TAGS
    tags = TAGS.copy()
    if tag and tag != cached_tag:
        if cached_tag:
            tags[cached_tag].remove(cached_match)
            if not tags[cached_tag]:
                del tags[cached_tag]
        if tag and match:
            if tag not in tags:
                tags[tag] = [match]
            else:
                tags[tag].append(match)
    elif match and match != cached_match:
        tags[tag].remove(cached_match)
        tags[tag].append(match)
    else:  # no diff
        return

    TAGS = tags
    with open(filepath, 'w+') as cfg:
        cfg.write(json.dumps(TAGS,
                  sort_keys=True, indent=4, separators=(',', ': ')))

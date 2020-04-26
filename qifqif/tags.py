#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Cache mapping categories with associated keywords"""

import json
import os
import re

from six import string_types

TAGS = dict()


def rulify(obj):
    """Convert rulelike object to a ruler"""
    if isinstance(obj, string_types):
        return {'PAYEE': r'\b%s\b' % obj} if obj else None
    return obj


def unrulify(ruler):
    """Convert regex payee rule to string"""
    if ruler and not isinstance(ruler, string_types):
        field = list(ruler.keys())[0]
        if field.isupper():
            # Basic rulers entered at first prompt are recognizable by the
            # uppercase dict key and should be unrulified to a string for the
            # sake of json readability.
            return ruler[field].strip(r'\b')
    elif ruler and ruler.isspace():
        return
    return ruler


def match(ruler, t):
    """Return a tuple (match, dict) indicating if transaction matches ruler.
       match is a bool, while dict contains matching values for ruler fields.
    """
    res = {}
    ruler = rulify(ruler)
    for field in ruler.keys():
        rule = ruler[field]
        field = field.lower()
        try:
            m = re.search(rule, t[field], re.I)
            res[field] = t[field][m.start():m.end()] if m else None
        except Exception:
            res[field] = None
    return all([x for x in list(res.values())]), res


def find_tag_for(t):
    """If transaction matches a rule, returns corresponding tuple
       (tag, ruler, match).
    """
    res = []
    for (tag, rulers) in list(TAGS.items()):
        for ruler in rulers:
            m, matches = match(ruler, t)
            if m:
                res.append((tag, ruler, matches))
    if res:
        # Return rule with the most fields.
        # If several, pick the ont with the longer rules.
        return max(res, key=lambda tag_ruler_matches: (len(list(rulify(
            tag_ruler_matches[1]).keys())), sum(
            [len(v) for v in list(tag_ruler_matches[2].values()) if v])))
    return None, None, None


def convert(tags):
    """Rulify all objects of given tags dict.
    """
    for (tag, rulers) in list(tags.items()):
        tags[tag] = []
        for ruler in rulers:
            tags[tag].append(rulify(ruler))
    return tags


def load(filepath):
    """Load tags dictionary.
    """
    global TAGS
    if os.path.isfile(filepath):
        with open(filepath, 'r') as cfg:
            try:
                TAGS = json.load(cfg)
            except Exception as err:
                print("Error loading '%s'.\n%s" % (filepath, err))
                exit(1)
    else:
        TAGS = {}
    return TAGS


def prettify(tags):
    """Format tags for json output.
    """
    return json.dumps(tags, sort_keys=True, indent=4,
                      separators=(',', ': ')) + '\n'


def save(filepath, tags):
    """Save tags dictionary on disk
    """
    with open(filepath, 'w+') as cfg:
        cfg.write(prettify(tags))


def edit(t, tag, _match, options=None):
    """Save a tag modification into dictionary and save the latter on file.
    """
    if not options:
        options = {}
    _match = unrulify(_match)
    cached_tag, cached_match, _ = find_tag_for(t)
    if tag != cached_tag:
        if cached_tag:
            TAGS[cached_tag].remove(cached_match)
            if not TAGS[cached_tag]:
                del TAGS[cached_tag]
        if tag and _match:
            if tag not in TAGS:
                TAGS[tag] = [_match]
            else:
                TAGS[tag].append(_match)
    elif _match is not None and _match != cached_match:
        if cached_match:
            TAGS[tag].remove(cached_match)
        if tag and _match:
            TAGS[tag].append(_match)
    else:  # no diff
        return

    if not options.get('dry-run', False):
        save(options['config'], TAGS)
    return TAGS

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Cache mapping categories with associated keywords"""

import json
import os
import re

TAGS = dict()


def rulify(obj):
    """Convert rulelike object to a ruler"""
    if isinstance(obj, basestring):
        return {'PAYEE': r'\b%s\b' % obj} if obj else None
    return obj


def unrulify(ruler):
    """Convert regex payee rule to string"""
    if ruler and not isinstance(ruler, basestring):
        field = ruler.keys()[0]
        if field.isupper():
            # Basic rulers entered at first prompt are recognizable by the
            # uppercase dict key and should be unrulified to a string for the
            # sake of json readability.
            return ruler[field].strip(r'\b')
    return ruler


def match(ruler, t):
    ruler = rulify(ruler)
    for field in ruler:
        try:
            if re.search(ruler[field], t[field.lower()], re.I) is None:
                return False, field.lower()
        except Exception:
            return False, field.lower()
    return True, None


def find_tag_for(t):
    """If transaction matches a rule, returns corresponding tuple
       (tag, rule).
    """
    res = []
    for (tag, rulers) in TAGS.items():
        for ruler in rulers:
            if match(ruler, t)[0]:
                res.append((tag, ruler))
    if res:
        # Return rule with the most fields.
        # If several, pick the ont with the longer rules.
        return max(res, key=lambda (tag, ruler): (len(rulify(ruler).keys()),
                   sum([len(v) for v in rulify(ruler).values()])))
    return None, None


def convert(tags):
    """Rulify all objects of given tags dict.
    """
    for (tag, rulers) in tags.items():
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
            except Exception as e:
                print("Error loading '%s'.\n%s" % (filepath, e))
                exit(1)
    else:
        TAGS = {}
    return TAGS


def save(filepath, tags):
    """Save tags dictionary on disk
    """
    with open(filepath, 'w+') as cfg:
        cfg.write(json.dumps(tags,
                  sort_keys=True, indent=4, separators=(',', ': ')) + '\n')


def edit(t, tag, match, options={}):
    """Save a tag modification into dictionary and save the latter on file.
    """

    global TAGS
    match = unrulify(match)
    cached_tag, cached_match = find_tag_for(t)
    if tag != cached_tag:
        if cached_tag:
            TAGS[cached_tag].remove(cached_match)
            if not TAGS[cached_tag]:
                del TAGS[cached_tag]
        if tag and match:
            if tag not in TAGS:
                TAGS[tag] = [match]
            else:
                TAGS[tag].append(match)
    elif match != cached_match:
        if cached_match:
            TAGS[tag].remove(cached_match)
        if tag and match:
            TAGS[tag].append(match)
    else:  # no diff
        return

    if not options.get('dry-run', False):
        save(options['config'], TAGS)
    return TAGS

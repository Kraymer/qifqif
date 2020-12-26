#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017-2020 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Enrich your QIF files with categories.
"""

from __future__ import print_function, unicode_literals

import argparse
import copy
import os
import sys
import io
import re
from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

from qifqif import tags, qifile
from qifqif.ui import complete_matches, colorize_match
from qifqif.terminal import TERM

ENCODING = "utf-8" if sys.stdin.encoding in (None, "ascii") else sys.stdin.encoding

__version__ = "0.7.3"


def quick_input(msg, choices="", sugg=None, clear=False):
    """raw_input wrapper that automates display of choices and return default
    choice when empty string entered.
    The prompt line(s) get cleared when done if clear is True.
    """
    if not sugg:
        sugg = []
    default = [x for x in choices if x[0].isupper()]
    default = default[0] if default else ""
    print(TERM.clear_eol, end="")
    msg = "%s%s" % (msg, (" [%s] ? " % ",".join(choices)) if choices else ": ")
    _input = prompt(
        msg,
        completer=WordCompleter(sugg, ignore_case=True,),
        complete_while_typing=False,
    )

    if _input in choices:
        _input = _input.upper()
    if clear:
        for _ in range(0, msg.count("\n") + 1):
            print(TERM.clear_last, end="")
    return _input or default


def query_cat(cached_cat):
    """Query category. If empty string entered then prompt to remove existing
    category, if any.
    """
    cat = quick_input("\nCategory", sugg=tags.TAGS.keys(), clear=True).strip()

    if not cat and cached_cat:
        erase = quick_input("\nRemove existing category", "yN", True)
        if erase.upper() == "N":
            cat = cached_cat
    return cat.strip() or None


def query_guru_ruler(t):
    """Define rules on a combination of fields. All rules must match
    corresponding fields for the ruler to be valid.
    """
    extras = sorted([k for (k, v) in t.items() if (v and not k.isdigit())])
    matchable_fields = sorted(set([x for x in t if t[x] and not x.isdigit()]) - {u"category",
        u"number"})

    guru_ruler = {}
    extras = {}
    field = True
    while field:
        # Enter field
        while True:
            # Update fields match indicators
            print(TERM.move_y(0))
            print_transaction(t, short=False, extras=extras)
            field = quick_input(
                "\nMatch on field", sugg=matchable_fields, clear=True
            ).lower()
            regex = "*" in field
            field = field.strip("*")
            if not field or field in matchable_fields:
                break
        # Enter match
        while field:
            print(TERM.move_y(0))
            print_transaction(t, short=False, extras=extras)
            existing_match = guru_ruler.get(field, "")
            ruler = quick_input(
                "\n%s match (%s)%s"
                % (
                    field.title(),
                    "regex" if regex else "chars",
                    " [%s]" % existing_match if existing_match else "",
                ),
                clear=True,
            )
            if ruler.isspace():  # remove field rule from ruler
                extras.pop(field, None)
                guru_ruler.pop(field, None)
            elif ruler:
                guru_ruler[field] = r"%s" % ruler if regex else re.escape(ruler)
            match, extras = check_ruler(guru_ruler, t)
            if match:
                break
    return guru_ruler


def query_basic_ruler(t, default_ruler):
    """Define basic rule consisting of matching full words on payee field.
    """
    default_field = u"payee"
    if not t[default_field]:
        return
    ruler = quick_input(
        "%s match %s"
        % (default_field.title(), "[%s]" % default_ruler if default_ruler else ""),
        sugg=complete_matches(t[default_field]),
    )
    ruler = tags.rulify(ruler)
    return ruler


def check_ruler(ruler, t):
    """Build fields status dict obtained by applying ruler to transaction."""
    extras = {}
    match, match_info = tags.match(ruler, t)
    for (key, val) in match_info.items():
        if not val:
            extras[key] = TERM.red("%s %s" % (TERM.KO, key.title()))
        else:
            extras[key] = TERM.green("%s %s" % (TERM.OK, key.title()))
    if not match:
        extras[u"category"] = TERM.red("%s Category" % TERM.KO)
    else:
        extras[u"category"] = TERM.green("%s Category" % TERM.OK)
    return match, extras


def query_ruler(t):
    """Prompt user to enter a valid matching ruler for transaction.
    First prompt is used to enter a basic ruler aka successive words to look
    for on payee line.
    This prompt can be skipped by pressing <Enter> to have access to guru
    ruler prompt, where ruler is a list of field/match to validate.
    """
    with TERM.fullscreen():
        extras = {}
        ok = False
        ruler = {}
        while True:
            print(TERM.move_y(0))
            print_transaction(t, extras=extras)
            if ok:
                break
            ruler = query_basic_ruler(t, tags.unrulify(ruler)) or query_guru_ruler(t)
            ok, extras = check_ruler(ruler, t)

    return ruler


def print_field(t, field, matches=None, extras=None):
    if not extras:
        extras = {}
    pad_width = 12
    fieldname = extras.get(field, "  " + field.title())
    line = TERM.clear_eol + "%s: %s" % (
        TERM.ljust(fieldname, pad_width, "."),
        colorize_match(t, field.lower(), matches) or TERM.red("<none>"),
    )
    print(line)


def print_transaction(t, short=True, extras=None):
    """Print transaction fields values and indicators about matchings status.
    If short is True, a limited set of fields is printed.
    extras dict can be used to add leading character to fields lines:
    - '✖' when the field don't match the prompted rule
    - '✔' when the field match the prompted rule
    - '+' when the category is fetched from .json matches file
    - ' ' when the category is present in input file
    """
    keys = (u"date", u"amount", u"payee", u"category") if short else list(t.keys())
    _, _, matches = tags.find_tag_for(t)
    for field in keys:
        if t[field] and not field.isdigit():
            print_field(t, field, matches, extras)
    print(TERM.clear_eos, end="")


def process_transaction(t, options):
    """Assign a category to a transaction.
    """
    cat, ruler = t[u"category"], None
    extras = {}

    if not t[u"category"]:  # Grab category from json cache
        cat, ruler, _ = tags.find_tag_for(t)
        if cat:
            t[u"category"] = cat
            extras = {u"category": "+ Category"}

    print_transaction(t, extras=extras)
    edit = options["force"] > 1 or (options["force"] and t[u"category"] not in tags.TAGS)
    audit = options["audit"]
    if t[u"category"]:
        if audit:
            msg = "\nEdit '%s' category" % TERM.green(t[u"category"])
            edit = quick_input(msg, "yN", clear=True) == "Y"
        if not edit:
            return t[u"category"], ruler

    # Query for category and overwrite category on screen
    if (not cat or edit) and not options["batch"]:
        t[u"category"] = query_cat(cat)
        # Query ruler if category entered or edit
        if t[u"category"]:
            ruler = query_ruler(t)
        extras = {u"category": TERM.OK + " Category"} if t[u"category"] else {}
        print(TERM.clear_last, end="")
        print_field(t, u"category", extras=extras)

    return t[u"category"], ruler


def parse_args(argv):
    """Build application argument parser and parse command line."""
    parser = argparse.ArgumentParser(
        description="Enrich your .QIF files with tags. "
        "See https://github.com/Kraymer/qifqif for more infos."
    )
    parser.add_argument(
        "src", metavar="QIF_FILE", help=".QIF file to process", default=""
    )
    audit_group = parser.add_mutually_exclusive_group()
    audit_group.add_argument(
        "-a",
        "--audit",
        dest="audit",
        action="store_true",
        help=("pause after each transaction"),
    )
    audit_group.add_argument(
        "-b",
        "--batch",
        action="store_true",
        dest="batch",
        help=("skip transactions that require user input"),
    )
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        help="configuration filename in json format. DEFAULT: ~/.qifqif.json",
        default=os.path.join(os.path.expanduser("~"), ".qifqif.json"),
    )
    dest_group = parser.add_mutually_exclusive_group()
    dest_group.add_argument(
        "-d",
        "--dry-run",
        dest="dry-run",
        action="store_true",
        help=("just print instead of writing file"),
    )
    parser.add_argument(
        "-f",
        "--force",
        action="count",
        default=0,
        help=(
            "ignore unknown categories and force editing of associated "
            "transactions. Repeat the flag (-ff) to force editing of all "
            "transactions."
        ),
    )
    dest_group.add_argument(
        "-o",
        "--output",
        dest="dest",
        help=("output filename. DEFAULT: edit input file in-place"),
        default="",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s " + __version__,
        help="display version information and exit",
    )
    args = vars(parser.parse_args(args=argv[1:]))
    if not args["dest"]:
        args["dest"] = args["src"]
    return args


def process_transactions(transactions, options):
    """Process file's transactions."""
    cat = None
    try:
        i = 0
        for (i, t) in enumerate(transactions):
            print("\n---")
            if not t[u"payee"]:
                print_transaction(t)
                print("Skip transaction #%s with no payee field" % (i + 1))
                continue
            cat, match = process_transaction(t, options)
            tags.edit(t, cat, match, options)
        i = i + 1
        if not options["batch"]:
            quick_input("\nPress any key to continue (Ctrl+D to discard " "edits)")
    except KeyboardInterrupt:
        return transactions[:i]
    return transactions[:i]


def main(argv=None):
    """Main function: Parse, process, print"""
    if argv is None:
        argv = sys.argv
    args = parse_args(argv)
    if not args:
        exit(1)
    original_tags = copy.deepcopy(tags.load(args["config"]))
    with io.open(args["src"], "r", encoding="utf-8", errors="ignore") as fin:
        lines = fin.readlines()
        transacs_orig = qifile.parse_lines(lines, options=args)
    try:
        transacs = process_transactions(transacs_orig, options=args)
    except EOFError:  # exit on Ctrl + D: restore original tags
        tags.save(args["config"], original_tags)
        return 1
    res = qifile.dump_to_buffer(transacs + transacs_orig[len(transacs):])
    if not args.get("dry-run"):
        with io.open(args["dest"], "w", encoding="utf-8") as dest:
            dest.write(res)
    if args["batch"] or args["dry-run"]:
        print("\n" + res)
    return 0 if len(transacs) == len(transacs_orig) else 1


if __name__ == "__main__":
    sys.exit(main())

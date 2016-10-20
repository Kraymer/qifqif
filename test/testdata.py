#!/usr/bin/env python

import io
import os
from qifqif import config, qifile


TAGS = {
    "Bars": ["Art Brut", "Sully"],
    "Clothes": ["Art Brut Shop"]
}
TRANSACTION = {
    'payee': 'CARTE 16/02/2014 Sully bar',
    'date': '16/02/2014',
    'memo': 'chouffe',
    '^': '^'
}
QIF_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
                        'rsrc', 'transac.qif')
CFG_FILE = os.path.join(os.path.realpath(os.path.dirname(__file__)),
    'rsrc', 'config.json')


def generate_lines(kinds):
    """Return lines corresponding to given fields ids sequence.
    """
    res = []
    for k in kinds:
        res.append(k + TRANSACTION[config.FIELDS.get(k, k)])
    return res


def transactions():
    with io.open(QIF_FILE, 'r', encoding='utf-8') as fin:
        lines = fin.readlines()
        return qifile.parse_lines(lines), lines

#!/usr/bin/env python

import qifqif


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


def generate_lines(kinds):
    """Return lines corresponding to given fields ids sequence.
    """
    res = []
    for k in kinds:
        res.append(k + TRANSACTION[qifqif.FIELDS.get(k, k)])
    return res

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from contextlib import contextmanager


class Terminus:
    """blessed Terminal ersatz for Windows exhibiting minimum features set"""

    @property
    def clear(self):
        return '\r'

    def __getattr__(self, name):
        def handler(*args, **kwargs):
            return '%s' % args
        return handler

    @contextmanager
    def fullscreen(self):
        yield None

    @contextmanager
    def location(self):
        yield None

try:
    from blessed import Terminal as BlessedTerminal

    class Terminal(BlessedTerminal):
        @property
        def clear(self):
            return self.move_up + self.move_x(0) + self.clear_eol
    TERM = Terminal()

except ImportError:
    TERM = Terminus()

    if sys.platform == 'win32':
        import codecs
        codecs.register(lambda name: codecs.lookup('utf-8')
                        if name == 'cp65001' else None)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2016 Fabrice Laporte - kray.me
# The MIT License http://www.opensource.org/licenses/mit-license.php

"""Wrapper around terminal capabilities"""

import sys
from contextlib import contextmanager


class Terminus(object):
    """blessed Terminal ersatz for Windows exhibiting minimum features set"""

    @property
    def clear(self):
        return '\r'

    def __getattr__(self, name):
        def handler(*args, **kwargs):
            return '%s' % (args or '')
        if 'clear' in name:
            return self.clear
        if 'move' in name:
            return lambda x: ''
        return handler

    def ljust(self, field, pad_width, fillchar):
        return field.ljust(pad_width - len(field), fillchar)

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
        def clear_last(self):
            return self.move_up + self.move_x(0) + self.clear_eol

        @property
        def undo(self):
            return 2 * self.clear

    TERM = Terminal()

except ImportError:
    TERM = Terminus()

    if sys.platform == 'win32':
        import codecs
        codecs.register(lambda name: codecs.lookup('utf-8')
                        if name == 'cp65001' else None)

        # use colorama to support "ANSI" terminal colors.
        try:
            import colorama
        except ImportError:
            pass
        else:
            colorama.init()

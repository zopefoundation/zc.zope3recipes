##############################################################################
#
# Copyright (c) 2006 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Zope 3 program entry points

$Id$
"""

import os, sys
import zope.app.debug
import zope.app.twisted.main
import zope.app.appsetup.interfaces
from zope.event import notify

def zglobals(args):
    options = zope.app.twisted.main.load_options(args)
    zope.app.appsetup.config(options.site_definition)
    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]
    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))
    
    db = zope.app.twisted.main.debug(args)
    if "PYTHONSTARTUP" in os.environ:
        execfile(os.environ["PYTHONSTARTUP"])
    
    app = zope.app.debug.Debugger.fromDatabase(db)
    return options, dict(
        app = app,
        debugger = app,
        root = app.root(),
        __name__ = '__main__',
        )

def debug(args):
    options, globs = zglobals(args[:2])
    args = options.args

    if args:
        sys.argv[:] = args
        globs['__file__'] = sys.argv[0]
        execfile(sys.argv[0], globs)
        sys.exit()
    else:
        import code
        code.interact(banner=banner, local=globs)

banner = """Welcome to the Zope 3 "debugger".
The application root object is available as the root variable.
A Zope debugger instance is available as the debugger (aka app) variable.
"""

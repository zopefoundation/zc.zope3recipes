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
"""

import os
import sys
import traceback

import six
import zope.app.debug
import zope.app.appsetup.interfaces
import zope.app.appsetup.product
from zope.event import notify


def load_options(args, main_module=None):
    options = main_module.ZopeOptions()
    options.schemadir = os.path.dirname(os.path.abspath(
        main_module.__file__))
    options.positional_args_allowed = True
    options.realize(args)

    if options.configroot.path:
        sys.path[:0] = [os.path.abspath(p) for p in options.configroot.path]
    return options


def zglobals(options):
    zope.app.appsetup.product.setProductConfigurations(options.product_config)
    zope.app.appsetup.config(options.site_definition)
    db = zope.app.appsetup.appsetup.multi_database(options.databases)[0][0]
    notify(zope.app.appsetup.interfaces.DatabaseOpened(db))

    globs = {"__name__": "__main__"}
    startup = os.environ.get("PYTHONSTARTUP")
    if startup:
        try:
            with open(startup) as f:
                globs["__file__"] = startup
                six.exec_(f.read(), globs)
                del globs["__file__"]
        except (OSError, IOError):
            # Not readable or not there, which is allowed.
            pass

    app = zope.app.debug.Debugger.fromDatabase(db)
    globs["app"] = app
    globs["debugger"] = app
    globs["root"] = app.root()

    return globs


def debug(args=None, main_module=None):
    if args is None:
        args = sys.argv[1:]

    options = load_options(args, main_module=main_module)
    if 'ZC_DEBUG_LOGGING' in os.environ:
        options.configroot.eventlog.startup()
    try:
        globs = zglobals(options.configroot)
    except Exception:
        if options.args:
            raise
        else:
            traceback.print_exc()
            import pdb
            pdb.post_mortem(sys.exc_info()[2])
            return

    args = options.args

    if args:
        sys.argv[:] = args
        globs['__file__'] = sys.argv[0]
        with open(sys.argv[0]) as f:
            code = compile(f.read(), sys.argv[0], 'exec')
            six.exec_(code, globs)
        sys.exit()
    else:
        import code
        code.interact(banner=banner, local=globs)


banner = """Welcome to the Zope 3 "debugger".
The application root object is available as the root variable.
A Zope debugger instance is available as the debugger (aka app) variable.
"""

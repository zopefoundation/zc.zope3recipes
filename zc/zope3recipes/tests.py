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

import os, re, shutil, sys, tempfile
import pkg_resources

import zc.buildout.testing

import unittest
import zope.testing
from zope.testing import doctest, renormalizing


def test_ctl():
    """
The ctl script is an extended version of zdaemon that provides an
extra command, run.  Let's create a buildout that installs it as an
ordinary script:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = ctl
    ...
    ... [ctl]
    ... recipe = zc.recipe.egg
    ... eggs = zc.zope3recipes
    ...        zdaemon
    ... entry-points = ctl=zc.zope3recipes.ctl:main
    ... scripts = ctl
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Installing ctl...
    Generated script '/sample-buildout/bin/ctl'.

We'll create a configuration file:

    >>> write('conf',
    ... '''
    ... <runner>
    ...   program echo hi
    ... </runner>
    ... ''')

The configuration doesn't matter much. :)

Unlike a normal zdaemon script, we have to pass two extra arguments, a
script to run the zope debugger with, and the name of a zope
configuration file. For demonstration purposes, we'll just use echo.

    >>> print system(join('bin', 'ctl')+' echo zope.conf -Cconf fg there'),
    echo hi there
    hi there

Notice:

  - The first 2 arguments were ignored.

  - It got the program, 'echo hi', from the configuration file.

  - We ran the program in the foreground, passing the extra argument, there.

Now, if we use the run command, it will run the script we passed as
the first argument:

    >>> print system(join('bin', 'ctl')+' echo zope.conf -Cconf run there'),
    -C zope.conf there

debug is another name for run:

    >>> print system(join('bin', 'ctl')+' echo zope.conf -Cconf debug there'),
    -C zope.conf there


"""

def test_sane_errors_from_recipe():
    """
There was a bug in the recipe error handling that caused errors to be hidden

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = instance
    ...
    ... [myapp]
    ... location = foo
    ... ;; Note that 'servers' has a default value when the
    ... ;; application recipe is involved.
    ... servers = twisted
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = 
    ... ''')

    >>> print system(join('bin', 'buildout')),
    Couldn't find index page for 'zc.recipe.egg' (maybe misspelled?)
    Installing instance.
    While:
      Installing instance.
    Error: No database sections have been defined.
    """

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('zc.zope3recipes', test)
    zc.buildout.testing.install('zope.testing', test)
    zc.buildout.testing.install('zc.recipe.egg', test)
    zc.buildout.testing.install('zdaemon', test)
    zc.buildout.testing.install('ZConfig', test)
    zc.buildout.testing.install('zc.recipe.filestorage', test)
    # prevent upgrade during test
    conf_dir = os.path.join(os.path.expanduser('~'), '.buildout')
    conf_file = os.path.join(conf_dir, 'default.cfg')
    if not os.path.exists(conf_dir):
        os.makedirs(conf_dir)
    if not os.path.exists(conf_file):
        open(conf_file, 'w').write("[buildout]\n"
                                   "newest = false")
    else:
        raise RuntimeWarning('Unable to set "newest=false" for tests')


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
    "Couldn't find index page for '[a-zA-Z0-9.]+' "
    "\(maybe misspelled\?\)"
    "\n"
    ), ''),
    (re.compile("""['"][^\n"']+zope3recipes[^\n"']*['"],"""),
     "'/zope3recipes',"),
    (re.compile('#![^\n]+\n'), ''),                
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    ])


def test_suite():
    suite = unittest.TestSuite()
    if sys.platform[:3].lower() == "win":
        suite.addTest(doctest.DocFileSuite('WINDOWS.txt',
                 setUp=setUp,
                 tearDown=zc.buildout.testing.buildoutTearDown,
                 checker=checker,
                 optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))
    else:
        suite.addTest(doctest.DocTestSuite(
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))
        suite.addTest(doctest.DocFileSuite('README.txt',
            setUp=setUp,
            tearDown=zc.buildout.testing.buildoutTearDown,
            checker=checker,
            optionflags = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

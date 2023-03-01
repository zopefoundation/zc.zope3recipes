##############################################################################
#
# Copyright Zope Foundation and Contributors.
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

import os

from setuptools import find_packages
from setuptools import setup


name = "zc.zope3recipes"
version = "1.0"


def read(*rnames):
    with open(os.path.join(os.path.dirname(__file__), *rnames)) as fp:
        return fp.read()


setup(
    name=name,
    version=version,
    author="Jim Fulton",
    author_email="zope-dev@zope.dev",
    description="ZC Buildout recipe for defining Zope 3 applications",
    license="ZPL 2.1",
    keywords="zope3 buildout",
    url='https://github.com/zopefoundation/%s' % name,
    long_description=(
        read('README.rst')
        + '\n' +
        read('CHANGES.rst')
        + '\n' +
        '========================\n'
        ' Detailed Documentation\n'
        '========================\n'
        + '\n' +
        read('src', 'zc', 'zope3recipes', 'README.rst').split('\n\n', 1)[1]
    ),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    namespace_packages=['zc'],
    python_requires='>=3.7',
    install_requires=[
        'zc.buildout >= 1.2.0',
        'zope.testing',
        'setuptools',
        'zc.recipe.egg >= 1.2.0',
        'ZConfig >= 2.4a5',
        "pywin32 ; platform_system=='Windows'",
    ],
    entry_points={
        'zc.buildout': [
             'application = %s.recipes:Application' % name,
             'app = %s.recipes:App' % name,
             'instance = %s.recipes:Instance' % name,
             'offline = %s.recipes:Offline' % name,
             'zopeconf = %s.recipes:ZopeConf' % name,
         ],
    },
    extras_require=dict(
        test=[
            'zdaemon >= 3.0.0',
            'zc.recipe.filestorage',
            'PasteScript',
        ],
    ),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

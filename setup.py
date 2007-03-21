import os
from setuptools import setup, find_packages

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

long_description = (
    read('README.txt')
    + '\n' +
    'Detailed Documentation\n'
    '**********************\n'
    + '\n' +
    read('zc', 'zope3recipes', 'README.txt')
    + '\n' +
    'Download\n'
    '**********************\n'
    )

#open('long-description.txt', 'w').write(long_description)

name = "zc.zope3recipes"
setup(
    name = name,
    version = "0.5.0",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for defining Zope 3 applications",
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.zope.org/'+name,
    long_description=long_description,

    packages = find_packages('.'),
    include_package_data = True,
    #package_dir = {'':'src'},
    namespace_packages = ['zc'],
    install_requires = ['zc.buildout', 'zope.testing', 'setuptools',
                        'zc.recipe.egg', 'ZConfig'],
    dependency_links = ['http://download.zope.org/distribution/'],
    entry_points = {
        'zc.buildout': [
             'app = %s.recipes:App' % name,
             'instance = %s.recipes:Instance' % name,
             ]
        },
    extras_require = dict(
        tests = ['zdaemon', 'zc.recipe.filestorage'],
        ),
    classifiers = [
       'Framework :: Buildout',
       'Intended Audience :: Developers',
       'License :: OSI Approved :: Zope Public License',
       'Topic :: Software Development :: Build Tools',
       'Topic :: Software Development :: Libraries :: Python Modules',
       ],
    )

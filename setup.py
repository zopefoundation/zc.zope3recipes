from setuptools import setup, find_packages

name = "zc.zope3recipes"
setup(
    name = name,
    version = "0.2",
    author = "Jim Fulton",
    author_email = "jim@zope.com",
    description = "ZC Buildout recipe for defining Zope 3 applications",
    #long_description = open('README.txt').read(),
    license = "ZPL 2.1",
    keywords = "zope3 buildout",
    url='http://svn.zope.org/'+name,

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
    )

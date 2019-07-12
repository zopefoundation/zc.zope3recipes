=============
Zope3 Recipes
=============

This documentation describes the windows installation. See README for more
general information.

The 'application' recipe accepts the following options:

site.zcml
  The contents of site.zcml.

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts.


Lets define some (bogus) eggs that we can use in our application:

    >>> mkdir('demo1')
    >>> write('demo1', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name = 'demo1')
    ... ''')

    >>> mkdir('demo2')
    >>> write('demo2', 'setup.py',
    ... '''
    ... from setuptools import setup
    ... setup(name = 'demo2', install_requires='demo1')
    ... ''')

We'll create a buildout.cfg file that defines our application:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:application
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

Now, Let's run the buildout and see what we get:

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

The runzope script runs the Web server:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

Here, unlike the above example the location path is not included
in sys.path .  Similarly debugzope script is also changed:

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zc.zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))


Building Zope 3 Applications (from Zope 3 checkouts/tarballs)
=============================================================

The 'app' recipe works much like the 'application' recipe.  It takes
the same configuration options plus the following one:

zope3
  The name of a section defining a location option that gives the
  location of a Zope installation.  This can be either a checkout or a
  distribution.  If the location has a lib/python subdirectory, it is
  treated as a distribution, otherwise, it must have a src
  subdirectory and will be treated as a checkout. This option defaults
  to "zope3".  And if location is empty, the application will run solely
  from eggs.

Let's look at an example.  We'll make a faux zope installation:

    >>> zope3 = tmpdir('zope3')
    >>> mkdir(zope3, 'src')

Now we'll create a buildout.cfg file that defines our application:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

Note that our site.zcml file is very small.  It expect the application
zcml to define almost everything.  In fact, a site.zcml file will often
include just a single include directive.  We don't need to include the
surrounding configure element, unless we want a namespace other than
the zope namespace.  A configure directive will be included for us.

Let's run the buildout and see what we get:

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

A directory is created in the parts directory for our application files:

    >>> ls('parts')
    d  myapp

    >>> ls('parts', 'myapp')
    -  debugzope-script.py
    -  debugzope.exe
    -  runzope-script.py
    -  runzope.exe
    -  site.zcml

We get 3 files, two scripts and a site.zcml file.  The site.zcml file
is just what we had in the buildout configuration:

    >>> cat('parts', 'myapp', 'site.zcml')
    <configure xmlns='http://namespaces.zope.org/zope'
               xmlns:meta="http://namespaces.zope.org/meta"
               >
    <include package="demo2" />
    <principal
    id="zope.manager"
    title="Manager"
    login="jim"
    password_manager="SHA1"
    password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    />
    <grant
    role="zope.Manager"
    principal="zope.manager"
    />
    </configure>

Unfortunately, the leading whitespace is stripped from the
configuration file lines.  This is a consequence of the way
ConfigParser works.

The runzope script runs the Web server:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

It includes in it's path the eggs we specified in the configuration
file, along with their dependencies. Note that we haven't specified a
configuration file.  When runzope is run, a -C option must be used to
provide a configuration file.  -X options can also be provided to
override configuration file options.

The debugzope script provides access to the object system.  When
debugzope is run, a -C option must be used to provide a configuration
file.  -X options can also be provided to override configuration file
options.  If run without any additional arguments, then an interactive
interpreter will be started with databases specified in the
configuration file opened and with the variable root set to the
application root object.  The debugger variable is set to a Zope 3
debugger.  If additional arguments are provided, then the first
argument should be a script name and the remaining arguments are
script arguments.  The script will be run with the root and debugger
variables available as global variables.

..

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      '/zc.zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.twisted.main))

Note that the runzope shown above uses the default, twisted-based
server components.  It's possible to specify which set of server
components is used: the "servers" setting can be set to either
"zserver" or "twisted".  For the application, this affects the runzope
script; we'll see additional differences when we create instances of
the application.

Let's continue to use the twisted servers, but make the selection
explicit:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = twisted
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Updating myapp.

Note that this is recognized as not being a change to the
configuration; the messages say that myapp was updated, not
uninstalled and then re-installed.

The runzope script generated is identical to what we saw before:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.twisted.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.twisted.main.main())

We can also specify the ZServer servers explicitly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = zserver
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

The part has been re-installed, and the runzope script generated is
different now.  Note that the main() function is imported from a
different package this time:

    >>> cat('parts', 'myapp', 'runzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      ]
    <BLANKLINE>
    import zope.app.server.main
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zope.app.server.main.main())

The debugzope script has also been modified to take this into account.

    >>> cat('parts', 'myapp', 'debugzope')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/demo2',
      '/sample-buildout/demo1',
      '/zope3/src',
      '/zc.zope3recipes',
      ]
    <BLANKLINE>
    import zope.app.server.main
    <BLANKLINE>
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.debugzope.debug(main_module=zope.app.server.main))


Legacy Functional Testing Support
---------------------------------

Zope 3's functional testing support is based on zope.testing test
layers. There is a default functional test layer that older functional
tests use.  This layer loads the default configuration for the Zope
application server.  It exists to provide support for older functional
tests that were written before layers were added to the testing
infrastructure.   The default testing layer has a number of
disadvantages:

- It loads configurations for a large number of packages.  This has
  the potential to introduce testing dependency on all of these
  packages.

- It required a ftesting.zcml file and makes assumptions about where
  that file is.  In particular, it assumes a location relative to the
  current working directory when the test is run.

Newer software and maintained software should use their own functional
testing layers that use test-configuration files defined in packages.

To support older packages that use the default layer, a ftesting.zcml
option is provided.  If it is used, then the contents of the option
are written to a ftesting.zcml file in the application.  In addition,
an ftesting-base.zcml file is written that includes configuration
traditionally found in a Zope 3 ftesting-base.zcml excluding reference
to package-includes.

If we modify our buildout to include an ftesting.zcml option:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = myapp
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... ftesting.zcml =
    ...    <meta:provides feature="devmode" />
    ...    <include file="ftesting-base.zcml" />
    ...    <includeOverrides package="demo2" />
    ... eggs = demo2
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.

We'll get ftesting.zcml files and ftesting-base.zcml files created in
the application:

    >>> cat('parts', 'myapp', 'ftesting.zcml')
    <configure xmlns='http://namespaces.zope.org/zope'
               xmlns:meta="http://namespaces.zope.org/meta"
               >
    <BLANKLINE>
    <meta:provides feature="devmode" />
    <include file="ftesting-base.zcml" />
    <includeOverrides package="demo2" />
    </configure>

    >>> cat('parts', 'myapp', 'ftesting-base.zcml')
    <BLANKLINE>
    <configure
       xmlns="http://namespaces.zope.org/zope"
       i18n_domain="zope"
       >
      <include package="zope.app" />
      <include package="zope.app" file="ftesting.zcml" />
      <include package="zope.app.securitypolicy" file="meta.zcml" />
      <include package="zope.app.securitypolicy" />
      <securityPolicy
        component="zope.app.securitypolicy.zopepolicy.ZopeSecurityPolicy" />
      <role id="zope.Anonymous" title="Everybody"
                     description="All users have this role implicitly" />
      <role id="zope.Manager" title="Site Manager" />
      <role id="zope.Member" title="Site Member" />
      <grant permission="zope.View"
                      role="zope.Anonymous" />
      <grant permission="zope.app.dublincore.view"
                      role="zope.Anonymous" />
      <grantAll role="zope.Manager" />
      <include package="zope.app.securitypolicy.tests"
               file="functional.zcml" />
      <unauthenticatedPrincipal
          id="zope.anybody"
          title="Unauthenticated User"
          />
      <unauthenticatedGroup
        id="zope.Anybody"
        title="Unauthenticated Users"
        />
      <authenticatedGroup
        id="zope.Authenticated"
        title="Authenticated Users"
        />
      <everybodyGroup
        id="zope.Everybody"
        title="All Users"
        />
      <principal
          id="zope.mgr"
          title="Manager"
          login="mgr"
          password="mgrpw" />
      <principal
          id="zope.globalmgr"
          title="Manager"
          login="globalmgr"
          password="globalmgrpw" />
      <grant role="zope.Manager" principal="zope.globalmgr" />
    </configure>

Defining Zope3 instances
========================

Having defined an application, we can define one or more instances of
the application.  We do this using the zc.zope3recipes instance
recipe.  The instance recipe has 2 modes, a development and a
production mode.  We'll start with the development mode.  In
development mode, a part directory will be created for each instance
containing the instance's configuration files. This directory will
also contain run-time files created by the instances, such as log
files or zdaemon socket files.

When defining an instance, we need to specify a zope.conf file.  The
recipe can do most of the work for us.  Let's look at a a basic
example:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

The application option names an application part.  The application
part will be used to determine the location of the site.zcml file and
the name of the control script to run.

We specified a zope.conf option which contains a start at our final
zope.conf file.  The recipe will add some bits we leave out.  The one
thing we really need to have is a database definition.  We simply
include the zconfig option from the database section, which we provide
as a file storage part using the zc.recipe.filestorage recipe.  The
filestorage recipe will create a directory to hold our database and
compute a zconfig option that we can use in our instance section.

Note that we've replaced the myapp part with the instance part.  The
myapp part will be included by virtue of the reference from the
instance part.

Let's run the buildout, and see what we get:

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling myapp.
    Installing database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.
    Generated script '/sample-buildout/bin/instance'.

We see that the database and myapp parts were included by virtue of
being referenced from the instance part.

We get new directories for our database and instance:

    >>> ls('parts')
    d  database
    d  instance
    d  myapp

The instance directory contains zdaemon.conf and zope.conf files:

    >>> ls('parts', 'instance')
    -  zdaemon.conf
    -  zope.conf

Let's look at the zope.conf file that was generated:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

This uses the twisted server types, since that's the default
configuration for Zope 3.  If we specify use of the ZServer servers,
the names of the server types are adjusted appropriately:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = zserver
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.


The generated zope.conf file now uses the ZServer server components
instead:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type WSGI-HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

The Twisted-based servers can also be specified explicitly:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... servers = twisted
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling myapp.
    Updating database.
    Installing myapp.
    Generated script '/sample-buildout/parts/myapp/runzope'.
    Generated script '/sample-buildout/parts/myapp/debugzope'.
    Installing instance.

The generated zope.conf file now uses the Twisted server components
once more:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

It includes the database definition that we provided in the zope.conf
option.  It has a site-definition option that names the site.zcml file
from our application directory.

We didn't specify any server or logging ZConfig sections, so some were
generated for us.

Note that, by default, the event-log output goes to standard output.
We'll say more about that when we talk about the zdaemon
configuration later.

If we specify a server section ourselves:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...    <server>
    ...        type PostmortemDebuggingHTTP
    ...        address 8080
    ...    </server>
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.

Then the section (or sections) we provide will be used and new ones
won't be added:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8080
      type PostmortemDebuggingHTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

If we just want to specify alternate ports or addresses, we can use
the address option which accepts zero or more address specifications:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081 foo.com:8082
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <server>
      address foo.com:8082
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

We can specify our own accesslog and eventlog configuration.  For
example, to send the event-log output to a file and suppress the
access log:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ...    <eventlog>
    ...      <logfile>
    ...        path ${buildout:parts-directory}/instance/event.log
    ...        formatter zope.exceptions.log.Formatter
    ...      </logfile>
    ...    </eventlog>
    ...    <accesslog>
    ...    </accesslog>
    ...
    ... address = 8081
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path /sample-buildout/parts/instance/event.log
      </logfile>
    </eventlog>
    <BLANKLINE>
    <accesslog>
    </accesslog>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>

Let's look at the zdaemon.conf file:

    >>> cat('parts', 'instance', 'zdaemon.conf')
    <runner>
      daemon on
      directory /sample-buildout/parts/instance
      program /sample-buildout/parts/myapp/runzope -C /sample-buildout/parts/instance/zope.conf
      socket-name /sample-buildout/parts/instance/zdaemon.sock
      transcript /sample-buildout/parts/instance/z3.log
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /sample-buildout/parts/instance/z3.log
      </logfile>
    </eventlog>

Here we see a fairly ordinary zdaemon.conf file.  The program option
refers to the runzope script in our application directory.  The socket
file, used for communication between the zdaemon command-line script
and the zademon manager is placed in the instance directory.

If you want to override any part of the generated zdaemon output,
simply provide a zdaemon.conf option in your instance section:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.

    >>> cat('parts', 'instance', 'zdaemon.conf')
    <runner>
      daemon off
      directory /sample-buildout/parts/instance
      program /sample-buildout/parts/myapp/runzope -C /sample-buildout/parts/instance/zope.conf
      socket-name /sample-buildout/parts/instance/sock
      transcript /dev/null
    </runner>
    <BLANKLINE>
    <eventlog>
    </eventlog>

In addition to the configuration files, a control script is generated
in the buildout bin directory:

    >>> ls('bin')
    -  buildout-script.py
    -  buildout.exe
    -  instance-script.py
    -  instance.exe

..

    >>> cat('bin', 'instance')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/site-packages',
      '/zc.zope3recipes',
      ]
    <BLANKLINE>
    import zc.zope3recipes.winctl
    <BLANKLINE>
    if __name__ == '__main__':
        sys.exit(zc.zope3recipes.winctl.main([
            '/sample-buildout/parts/myapp/debugzope',
            '/sample-buildout/parts/instance/zope.conf',
            '-C', '/sample-buildout/parts/instance/zdaemon.conf',
            ]+sys.argv[1:]
            ))

Some configuration sections can include a key multiple times; the ZEO
client section works this way.  When a key is given multiple times,
all values are included in the resulting configuration in the order in
which they're give in the input::

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf =
    ...     <zodb>
    ...       <zeoclient>
    ...         server 127.0.0.1:8001
    ...         server 127.0.0.1:8002
    ...       </zeoclient>
    ...     </zodb>
    ... address = 8081
    ... zdaemon.conf =
    ...     <runner>
    ...       daemon off
    ...       socket-name /sample-buildout/parts/instance/sock
    ...       transcript /dev/null
    ...     </runner>
    ...     <eventlog>
    ...     </eventlog>
    ...
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Uninstalling database.
    Updating myapp.
    Installing instance.

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <zeoclient>
        server 127.0.0.1:8001
        server 127.0.0.1:8002
      </zeoclient>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /sample-buildout/parts/instance/access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>


Log files
---------

The log file settings deserver some explanation.  The Zope event log
only captures output from logging calls.  In particular, it doesn't
capture startup errors written to standard error.  The zdaemon
transcript log is very useful for capturing this output.  Without it,
error written to standard error are lost when running as a daemon.
The default Zope 3 configuration in the past was to write the Zope
access and event log output to both files and standard output and to
define a transcript log.  This had the effect that the transcript
duplicated the contents of the event log and access logs, in addition
to capturing other output.  This was space inefficient.

This recipe's approach is to combine the zope and zdaemon event-log
information as well as Zope error output into a single log file.  We
do this by directing Zope's event log to standard output, where it is
useful when running Zope in foreground mode and where it can be
captured by the zdaemon transcript log.

Unix Deployments
----------------

The instance recipe provides support for Unix deployments, as provided
by the zc.recipe.deployment recipe.  A deployment part defines a number of
options used by the instance recipe:

etc-directory
    The name of the directory where configuration files should be
    placed.  This defaults to /etc/NAME, where NAME is the deployment
    name.

log-directory
    The name of the directory where application instances should write
    their log files.  This defaults to /var/log/NAME, where NAME is
    the deployment name.

run-directory
    The name of the directory where application instances should put
    their run-time files such as pid files and inter-process
    communication socket files.  This defaults to /var/run/NAME, where
    NAME is the deployment name.

rc-directory
    The name of the directory where run-control scripts should be
    installed.

logrotate-directory
    The name of the directory where logrotate configuration files should be
    installed.

user
    The name of a user that processes should run as.

The deployment recipe has to be run as root for various reasons, but
we can create a faux deployment by providing a section with the needed
data. Let's update our configuration to use a deployment.  We'll first
create a faux installation root:

    >>> root = tmpdir('root')
    >>> mkdir(root, 'etc')
    >>> mkdir(root, 'etc', 'myapp-run')
    >>> mkdir(root, 'etc', 'init.d')
    >>> mkdir(root, 'etc', 'logrotate.d')

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-run
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-run]
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

Here we've added a deployment section, myapp-run, and added a
deployment option to our instance part telling the instance recipe to
use the deployment.  If we rerun the buildout:

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Installing database.
    Updating myapp.
    Installing instance.
    Generated script '/root/etc/init.d/myapp-run-instance'.

The installer files will move.  We'll no-longer have the instance part:

    >>> ls('parts')
    d  database
    d  myapp

or the control script:

    >>> ls('bin')
    -  buildout-script.py
    -  buildout.exe
    -  instance-script.py
    -  instance.exe

Rather, we'll get our configuration files in the /etc/myapp-run directory:

    >>> ls(root, 'etc', 'myapp-run')
    -  instance-zdaemon.conf
    -  instance-zope.conf

Note that the instance name was added as a prefix to the file names,
since we'll typically have additional instances in the deployment.

The control script is in the init.d directory:

    >>> ls(root, 'etc', 'init.d')
    -  myapp-run-instance-script.py
    -  myapp-run-instance.exe

Note that the deployment name is added as a prefix of the control
script name.

The logrotate file is in the logrotate.d directory:

    >>> ls(root, 'etc', 'logrotate.d')
    -  myapp-run-instance


The configuration files have changed to reflect the deployment
locations:

    >>> cat(root, 'etc', 'myapp-run', 'instance-zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8081
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /root/var/log/myapp-run/instance-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>

    >>> cat(root, 'etc', 'myapp-run', 'instance-zdaemon.conf')
    <runner>
      daemon on
      directory /root/var/run/myapp-run
      program /sample-buildout/parts/myapp/runzope -C /root/etc/myapp-run/instance-zope.conf
      socket-name /root/var/run/myapp-run/instance-zdaemon.sock
      transcript /root/var/log/myapp-run/instance-z3.log
      user zope
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path /root/var/log/myapp-run/instance-z3.log
      </logfile>
    </eventlog>

    >>> cat(root, 'etc', 'logrotate.d', 'myapp-run-instance')
    /root/var/log/myapp-run/instance-z3.log {
      rotate 5
      weekly
      postrotate
        /root/etc/init.d/myapp-run-instance reopen_transcript
      endscript
    }


Defining multiple similar instances
-----------------------------------

Often you want to define multiple instances that differ only by one or
two options (e.g. an address).  The extends option lets you name a
section from which default options should be loaded.  Any options in
the source section not defined in the extending section are added to
the extending section.

Let's update our buildout to add a new instance:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... develop = demo1 demo2
    ... parts = instance instance2
    ...
    ... [zope3]
    ... location = %(zope3)s
    ...
    ... [myapp]
    ... recipe = zc.zope3recipes:app
    ... site.zcml = <include package="demo2" />
    ...             <principal
    ...                 id="zope.manager"
    ...                 title="Manager"
    ...                 login="jim"
    ...                 password_manager="SHA1"
    ...                 password="40bd001563085fc35165329ea1ff5c5ecbdbbeef"
    ...                 />
    ...             <grant
    ...                 role="zope.Manager"
    ...                 principal="zope.manager"
    ...                 />
    ... eggs = demo2
    ...
    ... [instance]
    ... recipe = zc.zope3recipes:instance
    ... application = myapp
    ... zope.conf = ${database:zconfig}
    ... address = 8081
    ... deployment = myapp-run
    ...
    ... [instance2]
    ... recipe = zc.zope3recipes:instance
    ... extends = instance
    ... address = 8082
    ...
    ... [database]
    ... recipe = zc.recipe.filestorage
    ...
    ... [myapp-run]
    ... etc-directory = %(root)s/etc/myapp-run
    ... rc-directory = %(root)s/etc/init.d
    ... logrotate-directory = %(root)s/etc/logrotate.d
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

    >>> print(system(join('bin', 'buildout')))
    Develop: '/sample-buildout/demo1'
    Develop: '/sample-buildout/demo2'
    Uninstalling instance.
    Updating database.
    Updating myapp.
    Installing instance.
    Installing instance2.
    Generated script '/root/etc/init.d/myapp-run-instance2'.

Now, we have the new instance configuration files:

    >>> ls(root, 'etc', 'myapp-run')
    -  instance-zdaemon.conf
    -  instance-zope.conf
    -  instance2-zdaemon.conf
    -  instance2-zope.conf

    >>> cat(root, 'etc', 'myapp-run', 'instance2-zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    </zodb>
    <BLANKLINE>
    <server>
      address 8082
      type HTTP
    </server>
    <BLANKLINE>
    <accesslog>
      <logfile>
        path /root/var/log/myapp-run/instance2-access.log
      </logfile>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    </eventlog>


test_winctl
-----------

The winctl script is an extended version of zdaemon that provides an
extra command, run.  Let's create a buildout that installs it as an
ordinary script:

    >>> write('buildout.cfg',
    ... '''
    ... [buildout]
    ... parts = winctl
    ...
    ... [winctl]
    ... recipe = zc.recipe.egg
    ... eggs = zc.zope3recipes
    ...        zdaemon
    ... entry-points = winctl=zc.zope3recipes.winctl:main
    ... scripts = winctl
    ... ''')

    >>> print(system(join('bin', 'buildout')))
    Uninstalling instance2.
    Uninstalling instance.
    Uninstalling myapp.
    Uninstalling database.
    Installing winctl.
    Generated script '/sample-buildout/bin/winctl'.

We'll create a configuration file:

    >>> write('doecho.bat', 'echo %*')

    >>> write('conf',
    ... '''
    ... <runner>
    ...   program doecho.bat hi
    ... </runner>
    ... ''')

The configuration doesn't matter much. :)

Unlike a normal zdaemon script, we have to pass two extra arguments, a
script to run the zope debugger with, and the name of a zope
configuration file. For demonstration purposes, we'll just use echo.

confPath = os.path.abspath(conf)

    >>> conf = join(sample_buildout, 'conf')
    >>> echo = join(sample_buildout, 'doecho.bat')
    >>> cmd = '%s %s zope.conf -C%s fg there' % (join('bin', 'winctl'), echo, conf)
    >>> print(system(cmd)) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    <BLANKLINE>
    /sample-buildout>echo hi there
    hi there
    Zope3 started in forground:  doecho.bat hi there
    <BLANKLINE>

Notice:

  - The first 2 arguments were ignored.

  - It got the program, 'echo.bat hi', from the configuration file.

  - We ran the program in the foreground, passing the extra argument, there.

Now, if we use the run command, it will run the script we passed as
the first argument:

    >>> cmd = '%s %s zope.conf -C%s run there' % (join('bin', 'winctl'), echo, conf)
    >>> print(system(cmd)) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    <BLANKLINE>
    /sample-buildout>echo -C zope.conf there
    -C zope.conf there
    Debug Zope3:  /sample-buildout/doecho.bat -C zope.conf there
    Zope3 started in debug mode, pid=...
    <BLANKLINE>

debug is another name for run:

    >>> cmd = '%s %s zope.conf -C%s debug there' % (join('bin', 'winctl'), echo, conf)
    >>> print(system(cmd)) #doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    <BLANKLINE>
    /sample-buildout>echo -C zope.conf there
    -C zope.conf there
    Debug Zope3:  /sample-buildout/doecho.bat -C zope.conf there
    Zope3 started in debug mode, pid=...
    <BLANKLINE>

test_sane_errors_from_recipe
----------------------------

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

    >>> print(system(join('bin', 'buildout')))
    Couldn't find index page for 'zc.recipe.egg' (maybe misspelled?)
    Uninstalling winctl.
    Installing instance.
    While:
      Installing instance.
    Error: No database sections have been defined.

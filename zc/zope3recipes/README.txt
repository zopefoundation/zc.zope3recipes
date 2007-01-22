=============
Zope3 Recipes
=============

The Zope 3 recipes allow one to define Zope applications and instances
of those applications.  A Zope application is a collection of software
and software configuration, expressed as ZCML.  A Zope instance
invokes the application with a specific instance configuration.  A
single application may have many instances.

Building Zope 3 Applications
============================

The "app" recipe is used to define a Zope application.  It is designed
to work with classic Zope releases. (In the future, there will be an
"application" recipe that will work with Zope soley as eggs.)  The app
recipe causes a part to be created. The part will contain the scripts
runzope and debugzope and the application's site.zcml.  Both of the
scripts will require providing a -C option and the path to a zope.conf
file when run.  The debugzope script can be run with a script name and
arguments, in which case it will run the script, rather than starting
an interactive session.

The app recipe accepts the following options:

zope3
  The name of a section defining a location option that gives the
  location of a Zope installation.  This can be either a checkout or a
  distribution.  If the location has a lib/python subdirectory, it is
  treated as a distribution, othwerwise, it must have a src
  subdirectory and will be treated as a checkout. This option defaults
  to "zope3".

site.zcml
  The contents of site.zcml.

eggs
  The names of one or more eggs, with their dependencies that should
  be included in the Python path of the generated scripts. 

Let's look at an example.  We'll make a faux zope installation:

    >>> zope3 = tmpdir('zope3')
    >>> mkdir(zope3, 'src')

We'll also define some (bogus) eggs that we can use in our
application:

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
zcml to define amost everything.  In fact, a site.zcml file will often
include just a single include directive.  We don't need to include the
surrounding configure element, unless we want a namespace other than
the zope namespace.  A configure directive will be included for us.

Let's run the buildout and see what we get:

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Installing myapp

A directory is created in the parts directory for our application files:

    >>> ls('parts')
    d  myapp

    >>> ls('parts', 'myapp')
    -  debugzope
    -  runzope
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
        zope.app.twisted.main.main()

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
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zc.zope3recipes.debugzope
    <BLANKLINE>
    if __name__ == '__main__':
        zc.zope3recipes.debugzope.debug()

Legacy Functional Testing Support
---------------------------------

Zope 3's functional testing support is based on zope.testing test
layers. There is a default functional test layer that older functional
tests use.  This layer loads the default configueration for the Zope
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

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling myapp
    buildout: Installing myapp

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

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling myapp
    buildout: Installing database
    buildout: Installing myapp
    buildout: Installing instance

We see thatthe database and myapp parts were included by virtue of
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
    <BLANKLINE>
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
    <BLANKLINE>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    <BLANKLINE>
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

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling instance
    buildout: Updating database
    buildout: Updating myapp
    buildout: Installing instance

Then the section (or sections) we provide will be used and new ones
won't be added:

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    <BLANKLINE>
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
    <BLANKLINE>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    <BLANKLINE>
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

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling instance
    buildout: Updating database
    buildout: Updating myapp
    buildout: Installing instance

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    <BLANKLINE>
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
    <BLANKLINE>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    <BLANKLINE>
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

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling instance
    buildout: Updating database
    buildout: Updating myapp
    buildout: Installing instance

    >>> cat('parts', 'instance', 'zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    <BLANKLINE>
    </zodb>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path /sample-buildout/parts/instance/event.log
      </logfile>
    <BLANKLINE>
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
    <BLANKLINE>
    </eventlog>

Here we see a fairly ordinary zdaemon.conf file.  The program option
refers to the runzope script in our application directory.  The socket
file, used for communication between the zdaemon command-line script
and the zademon manager is placed in the instance directory.

If you want to overrise any part of the generated zdaemon output,
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

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling instance
    buildout: Updating database
    buildout: Updating myapp
    buildout: Installing instance

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
    -  buildout
    -  instance

..

    >>> cat('bin', 'instance')
    #!/usr/local/bin/python2.4
    <BLANKLINE>
    import sys
    sys.path[0:0] = [
      '/sample-buildout/eggs/zdaemon-2.0-py2.4.egg',
      '/sample-buildout/eggs/setuptools-0.6-py2.4.egg',
      '/sample-buildout/eggs/ZConfig-2.3-py2.4.egg',
      '/zope3recipes',
      ]
    <BLANKLINE>
    import zc.zope3recipes.ctl
    <BLANKLINE>
    if __name__ == '__main__':
        zc.zope3recipes.ctl.main([
            '/sample-buildout/parts/myapp/debugzope',
            '/sample-buildout/parts/instance/zope.conf',
            '-C', '/sample-buildout/parts/instance/zdaemon.conf',
            ]+sys.argv[1:]
            )

Log files
---------

The log file settings deserver some explanation.  The Zope event log
only captures output from logging calls.  In particular, it doesn't
capture startup errors written to standard error.  The zdaemon
transcript log is very useful for capturing this output.  Without it,
error written to standard error are lost when running as a deamon.
The default Zope 3 configuration in the past was to write the Zope
access and event log output to both files and standard output and to
define a transcript log.  This had the effect that the transacript
duplicated the contents of the event log and access logs, in addition
to capturing other output.  This was space inefficient.

This recipe's approach is to combine the zope and zdaemon event-log
information as well as Zope error output into a single log file.  We
do this by directing Zope's event log to standard output, where it is
useful when running Zope in foreground mode and where it can be
captured by the zdaemon transscript log.

Unix Deployments
----------------

The instance recipe provides support for Unix deployments, as provided
by the zc.recipe.deployment recipe.  A deployment part defines a number of
options used by the instance recipe:

etc-directory
    The name of the directory where configurtion files should be
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
    ... log-directory = %(root)s/var/log/myapp-run
    ... run-directory = %(root)s/var/run/myapp-run
    ... user = zope
    ... ''' % globals())

Here we've added a deployment section, myapp-run, and added a
deployment option to our instance part telling the instance recipe to
use the deployment.  If we rerun the buildout:

    >>> print system(join('bin', 'buildout')),
    buildout: Develop: /sample-buildout/demo1
    buildout: Develop: /sample-buildout/demo2
    buildout: Uninstalling instance
    buildout: Updating database
    buildout: Updating myapp
    buildout: Installing instance

The installe files will move.  We'll no-longer have the instance part:

    >>> ls('parts')
    d  database
    d  myapp

or the control script:

    >>> ls('bin')
    -  buildout

Rather, we'll get our configuration files in the /etc/myapp-run directory:

    >>> ls(root, 'etc', 'myapp-run')
    -  instance-zdaemon.conf
    -  instance-zope.conf

Note that the instance name was added as a prefix to the file names,
since we'll typically have additional instances in the deployment.

The control script is in the init.d directory:

    >>> ls(root, 'etc', 'init.d')
    -  myapp-run-instance

Note that the deployment name is added as a prefix of the control
script name.

The configuration files have changed to reflect the deployment
locations:

    >>> cat(root, 'etc', 'myapp-run', 'instance-zope.conf')
    site-definition /sample-buildout/parts/myapp/site.zcml
    <BLANKLINE>
    <zodb>
      <filestorage>
        path /sample-buildout/parts/database/Data.fs
      </filestorage>
    <BLANKLINE>
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
    <BLANKLINE>
    </accesslog>
    <BLANKLINE>
    <eventlog>
      <logfile>
        formatter zope.exceptions.log.Formatter
        path STDOUT
      </logfile>
    <BLANKLINE>
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
    <BLANKLINE>
    </eventlog>

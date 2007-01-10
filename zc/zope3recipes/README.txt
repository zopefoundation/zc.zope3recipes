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

A directory is created in the parts directory for out application files:

    >>> ls('parts')
    d  myapp

    >>> ls('parts', 'myapp')
    -  debugzope
    -  runzope
    -  site.zcml

We get 3 files, two scripts and a site.zcml file.  The site.zcml file
is just what we had in the buildout configuration:

    >>> cat('parts', 'myapp', 'site.zcml')
    <configure xmlns='http://namespaces.zope.org/zope'>
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
        zc.zope3recipes.debugzope.main()
    
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
    buildout: Installing database
    buildout: Updating myapp
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
      program /sample-buildout/parts/myapp/runzope -C /sample-buildout/parts/instance/zope.conf
      socket-name /sample-buildout/parts/instance/zopectl.sock
      transcript /sample-buildout/parts/instance/z3.log
    </runner>
    <BLANKLINE>
    <eventlog>
      <logfile>
        path z3.log
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

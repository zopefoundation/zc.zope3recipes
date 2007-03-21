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
"""Collected Zope 3 recipes
"""

import os, shutil
import zc.buildout
import zc.recipe.egg
import pkg_resources
import ZConfig.cfgparser
import cStringIO

this_loc = pkg_resources.working_set.find(
    pkg_resources.Requirement.parse('zc.zope3recipes')).location

server_types = {
    # name     (module,                  http-name)
    'twisted': ('zope.app.twisted.main', 'HTTP'),
    'zserver': ('zope.app.server.main',  'WSGI-HTTP'),
    }


class App:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        location = buildout[options.get('zope3', 'zope3')]['location']
        if location:
            options['zope3-location'] = os.path.join(
                buildout['buildout']['directory'],
                location,
                )

        options['servers'] = options.get('servers', 'twisted')
        if options['servers'] not in server_types:
            raise ValueError(
                'servers setting must be one of "twisted" or "zserver"')

        options['scripts'] = ''
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

    def install(self):
        options = self.options

        try:
            z3path = options['zope3-location']
        except KeyError:
            path = ''
        else:
            if not os.path.exists(z3path):
                logger.error("The directory, %r, doesn't exist." % z3path)
                raise zc.buildout.UserError("No directory:", z3path)

            path = os.path.join(z3path, 'lib', 'python')
            if not os.path.exists(path):
                path = os.path.join(z3path, 'src')
                if not os.path.exists(path):
                    logger.error(
                        "The directory, %r, isn't a valid checkout or release."
                        % z3)
                    raise zc.buildout.UserError(
                        "Invalid Zope 3 installation:", z3path)

        dest = options['location']
        if not os.path.exists(dest):
            os.mkdir(dest)
            created = True
        else:
            created = False
            
        try:
            open(os.path.join(dest, 'site.zcml'), 'w').write(
                site_zcml_template % self.options['site.zcml']
                )

            extra = options.get('extra-paths')
            if extra:
                extra += '\n' + path
            else:
                extra = path
            options['extra-paths'] = extra

            self.egg.install()
            requirements, ws = self.egg.working_set()

            # install subprograms and ctl scripts
            server_module = server_types[options['servers']][0]
            zc.buildout.easy_install.scripts(
                [('runzope', server_module, 'main')],
                ws, options['executable'], dest,
                extra_paths = options['extra-paths'].split(),
                )

            options['extra-paths'] = extra + '\n' + this_loc

            zc.buildout.easy_install.scripts(
                [('debugzope', 'zc.zope3recipes.debugzope', 'debug')],
                ws, options['executable'], dest,
                extra_paths = options['extra-paths'].split(),
                )

            ftesting_zcml = options.get('ftesting.zcml')
            if ftesting_zcml:
                open(os.path.join(dest, 'ftesting.zcml'), 'w'
                     ).write(site_zcml_template % ftesting_zcml)
                open(os.path.join(dest, 'ftesting-base.zcml'), 'w'
                     ).write(ftesting_base)

            return dest

        except:
            if created:
                shutil.rmtree(dest)
            raise
        
        return dest

    update = install

site_zcml_template = """\
<configure xmlns='http://namespaces.zope.org/zope'
           xmlns:meta="http://namespaces.zope.org/meta"
           >
%s
</configure>
"""

class Instance:
    
    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        for section in options.get('extends', '').split():
            options.update(
                [(k, v) for (k, v) in buildout[section].items()
                 if k not in options
                 ])

        options['application-location'] = buildout[options['application']
                                                   ]['location']

        options['scripts'] = ''
        options['servers'] = buildout[options['application']]['servers']
        options['eggs'] = options.get('eggs', 'zdaemon\nsetuptools')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)

        deployment = self.deployment = options.get('deployment')
        if deployment:
            options['bin-directory'] = buildout[deployment]['rc-directory']
            options['run-directory'] = buildout[deployment]['run-directory']
            options['log-directory'] = buildout[deployment]['log-directory']
            options['etc-directory'] = buildout[deployment]['etc-directory']
            options['user'] = buildout[deployment]['user']
        else:
            options['bin-directory'] = buildout['buildout']['bin-directory']
            options['run-directory'] = os.path.join(
                buildout['buildout']['parts-directory'],
                self.name,
                )
            
    def install(self):
        options = self.options
        run_directory = options['run-directory']
        deployment = self.deployment
        if deployment:
            zope_conf_path = os.path.join(options['etc-directory'],
                                          self.name+'-zope.conf')
            zdaemon_conf_path = os.path.join(options['etc-directory'],
                                             self.name+'-zdaemon.conf')
            event_log_path = os.path.join(options['log-directory'],
                                          self.name+'-z3.log')
            access_log_path = os.path.join(options['log-directory'],
                                           self.name+'-access.log')
            socket_path = os.path.join(run_directory,
                                       self.name+'-zdaemon.sock')
            rc = deployment + '-' + self.name
            creating = [zope_conf_path, zdaemon_conf_path,
                        os.path.join(options['bin-directory'], rc),
                        ]
        else:
            zope_conf_path = os.path.join(run_directory, 'zope.conf')
            zdaemon_conf_path = os.path.join(run_directory, 'zdaemon.conf')
            event_log_path = os.path.join(run_directory, 'z3.log')
            access_log_path = os.path.join(run_directory, 'access.log')
            socket_path = os.path.join(run_directory, 'zdaemon.sock')
            rc = self.name
            creating = [run_directory,
                        os.path.join(options['bin-directory'], rc),
                        ]
            if not os.path.exists(run_directory):
                os.mkdir(run_directory)

        try:
            app_loc = options['application-location']

            zope_conf = options.get('zope.conf', '')+'\n'
            zope_conf = ZConfigParse(cStringIO.StringIO(zope_conf))

            zope_conf['site-definition'] = os.path.join(app_loc, 'site.zcml')

            server_type = server_types[options['servers']][1]
            for address in options.get('address', '').split():
                zope_conf.sections.append(
                    ZConfigSection('server',
                                   data=dict(type=server_type,
                                             address=address,
                                             ),
                                   )
                    )
            if not [s for s in zope_conf.sections
                    if ('server' in s.type)]:
                zope_conf.sections.append(
                    ZConfigSection('server',
                                   data=dict(type=server_type,
                                             address='8080',
                                             ),
                                   )
                    )

            if not [s for s in zope_conf.sections if s.type == 'zodb']:
                raise zc.buildout.UserError(
                    'No database sections have been defined.')

            if not [s for s in zope_conf.sections if s.type == 'accesslog']:
                zope_conf.sections.append(access_log(access_log_path))

            if not [s for s in zope_conf.sections if s.type == 'eventlog']:
                zope_conf.sections.append(event_log('STDOUT'))


            zdaemon_conf = options.get('zdaemon.conf', '')+'\n'
            zdaemon_conf = ZConfigParse(cStringIO.StringIO(zdaemon_conf))

            defaults = {
                'program': "%s -C %s" % (os.path.join(app_loc, 'runzope'),
                                         zope_conf_path,
                                         ),
                'daemon': 'on',
                'transcript': event_log_path,
                'socket-name': socket_path,
                'directory' : run_directory,
                }
            if deployment:
                defaults['user'] = options['user']
            runner = [s for s in zdaemon_conf.sections
                      if s.type == 'runner']
            if runner:
                runner = runner[0]
            else:
                runner = ZConfigSection('runner')
                zdaemon_conf.sections.insert(0, runner)
            for name, value in defaults.items():
                if name not in runner:
                    runner[name] = value

            if not [s for s in zdaemon_conf.sections
                    if s.type == 'eventlog']:
                # No database, specify a default one
                zdaemon_conf.sections.append(event_log2(event_log_path))

            zdaemon_conf = str(zdaemon_conf)

            self.egg.install()
            requirements, ws = self.egg.working_set()

            open(zope_conf_path, 'w').write(str(zope_conf))
            open(zdaemon_conf_path, 'w').write(str(zdaemon_conf))

            zc.buildout.easy_install.scripts(
                [(rc, 'zc.zope3recipes.ctl', 'main')],
                ws, options['executable'], options['bin-directory'],
                extra_paths = [this_loc],
                arguments = ('['
                             '\n        %r,'
                             '\n        %r,'
                             '\n        %r, %r,'
                             '\n        ]+sys.argv[1:]'
                             '\n        '
                             % (os.path.join(app_loc, 'debugzope'),
                                zope_conf_path,
                                '-C', zdaemon_conf_path,
                                )
                             ),
                )

            return creating

        except:
            for f in creating:
                if os.path.isdir(f):
                    shutil.rmtree(f)
                elif os.path.exists(f):
                    os.remove(f)
            raise


    update = install

def access_log(path):
    return ZConfigSection(
        'accesslog', '',
        sections=[ZConfigSection('logfile', '', dict(path=path))]
        )

def event_log(path, *data):
    return ZConfigSection(
        'eventlog', '', None,
        [ZConfigSection('logfile', '',
                        dict(path=path,
                             formatter='zope.exceptions.log.Formatter',
                             )
                        )
         ],
        )

def event_log2(path, *data):
    return ZConfigSection(
        'eventlog', '', None,
        [ZConfigSection('logfile', '',
                        dict(path=path,
                             )
                        )
         ],
        )

   
server_template = """
<server>
  type HTTP
  address %s
</server>
"""

access_log_template = """
<accesslog>
  <logfile>
    path %s
  </logfile>
</accesslog>
"""

event_log_template = """
<eventlog>
  <logfile>
    path %s
    formatter zope.exceptions.log.Formatter
  </logfile>
</eventlog>
"""

class ZConfigResource:

    def __init__(self, file, url=''):
        self.file, self.url = file, url

class ZConfigSection(dict):

    def __init__(self, type='', name='', data=None, sections=None):
        dict.__init__(self)
        if data:
            self.update(data)
        self.sections = sections or []
        self.type, self.name = type, name

    def addValue(self, key, value, *args):
        self[key] = value

    def __str__(self, pre=''):
        result = []
        if self.type:
            if self.name:
                result = ['%s<%s %s>' % (pre, self.type, self.name)]
            else:
                result = ['%s<%s>' % (pre, self.type)]
            pre += '  '

        for name, value in sorted(self.items()):
            result.append('%s%s %s' % (pre, name, value))

        if self.sections and self:
            result.append('')

        for section in self.sections:
            result.append(section.__str__(pre))
        
        if self.type:
            result.append('%s</%s>' % (pre[:-2], self.type))
            result.append('')
                          
        return '\n'.join(result).rstrip()+'\n'
  
class ZConfigContext:

    def __init__(self):
        self.top = ZConfigSection()
        self.sections = []

    def startSection(self, container, type, name):
        newsec = ZConfigSection(type, name)
        container.sections.append(newsec)
        return newsec

    def endSection(self, container, type, name, newsect):
        pass

    def importSchemaComponent(self, pkgname):
        pass

    def includeConfiguration(self, section, newurl, defines):
        raise NotImplementedError('includes are not supported')

def ZConfigParse(file):
    c = ZConfigContext()
    ZConfig.cfgparser.ZConfigParser(ZConfigResource(file), c).parse(c.top)
    return c.top

ftesting_base = """
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
"""

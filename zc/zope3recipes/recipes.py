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

class App:

    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        z3path = options['zope3-location'] = os.path.join(
            buildout['buildout']['directory'],
            buildout[options.get('zope3', 'zope3')]['location'],
            )

        if not os.path.exists(z3path):
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

        self.zpath = path
        options['scripts'] = ''
        self.egg = zc.recipe.egg.Egg(buildout, name, options)


    def install(self):
        options = self.options
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
            zpath = self.zpath
            if extra:
                extra += '\n' + zpath
            else:
                extra = zpath
            options['extra-paths'] = extra

            self.egg.install()
            requirements, ws = self.egg.working_set()

            # install subprograms and ctl scripts
            zc.buildout.easy_install.scripts(
                [('runzope', 'zope.app.twisted.main', 'main')],
                ws, options['executable'], dest,
                extra_paths = options['extra-paths'].split(),
                )

            options['extra-paths'] = extra + '\n' + this_loc

            zc.buildout.easy_install.scripts(
                [('debugzope', 'zc.zope3recipes.debugzope', 'main')],
                ws, options['executable'], dest,
                extra_paths = options['extra-paths'].split(),
                )

            return dest

        except:
            if created:
                shutil.rmtree(dest)
            raise
        
        return dest

    update = install

site_zcml_template = """<configure xmlns='http://namespaces.zope.org/zope'>
%s
</configure>
"""

class Instance:
    
    def __init__(self, buildout, name, options):
        self.name, self.options = name, options

        options['location'] = os.path.join(
            buildout['buildout']['parts-directory'],
            self.name,
            )

        options['application-location'] = buildout[options['application']
                                                   ]['location']

        options['bin-directory'] = buildout['buildout']['bin-directory']

        options['scripts'] = ''
        options['eggs'] = options.get('eggs', 'zdaemon\nsetuptools')
        self.egg = zc.recipe.egg.Egg(buildout, name, options)
            

    def install(self):
        options = self.options
        dest = conf_dir = log_dir = run_dir = options['location']
        app_loc = options['application-location']

        zope_conf_path = os.path.join(dest, 'zope.conf')
        zdaemon_conf_path = os.path.join(dest, 'zdaemon.conf')

        zope_conf = options.get('zope.conf', '')+'\n'
        zope_conf = ZConfigParse(cStringIO.StringIO(zope_conf))
        
        zope_conf['site-definition'] = os.path.join(app_loc, 'site.zcml')

        for address in options.get('address', '').split():
            zope_conf.sections.append(
                ZConfigSection('server',
                               data=dict(type='HTTP',
                                         address=address,
                                         ),
                               )
                )
        if not [s for s in zope_conf.sections
                if ('server' in s.type)]:
            zope_conf.sections.append(
                ZConfigSection('server',
                               data=dict(type='HTTP',
                                         address='8080',
                                         ),
                               )
                )

        if not [s for s in zope_conf.sections if s.type == 'zodb']:
            raise zc.buildout.UserError(
                'No database sections have been defined.')

        if not [s for s in zope_conf.sections
                if s.type == 'accesslog']:
            zope_conf.sections.append(
                access_log(os.path.join(log_dir, 'access.log')))

                
        if not [s for s in zope_conf.sections
                if s.type == 'eventlog']:
            zope_conf.sections.append(event_log('STDOUT'))


        zdaemon_conf = options.get('zdaemon.conf', '')+'\n'
        zdaemon_conf = ZConfigParse(cStringIO.StringIO(zdaemon_conf))

        defaults = {
            'program': "%s -C %s" % (os.path.join(app_loc, 'runzope'),
                                     zope_conf_path,
                                     ),
            'daemon': 'on',
            'transcript': os.path.join(log_dir, 'z3.log'),
            'socket-name': os.path.join(run_dir, 'zopectl.sock'),
            }
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
            zdaemon_conf.sections.append(event_log2('z3.log'))

        zdaemon_conf = str(zdaemon_conf)

        self.egg.install()
        requirements, ws = self.egg.working_set()

        if not os.path.exists(dest):
            os.mkdir(dest)
            created = True
        else:
            created = False
            
        try:
            open(zope_conf_path, 'w').write(str(zope_conf))
            open(zdaemon_conf_path, 'w').write(str(zdaemon_conf))

            zc.buildout.easy_install.scripts(
                [(self.name, 'zc.zope3recipes.ctl', 'main')],
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

        except:
            if created:
                shutil.rmtree(dest)
            raise

        return dest, os.path.join(options['bin-directory'], self.name)

    def update(self):
        pass


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

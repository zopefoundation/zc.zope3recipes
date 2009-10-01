**************************************
Zope3 Application and Instance Recipes
**************************************

Recipes for creating Zope 3 instances with distinguishing features:

- Don't use a skeleton

- Separates application and instance definition

- Don't support package-includes

Unfortunately, partial Windows support at this time. It works but it's alpha.

.. contents::

Releases
********

===================
0.12.0 (unreleased)
===================

- Nothing yet.


===================
0.11.0 (2009/10/01)
===================

- Added support and tests for relative paths buildout option.
- Changed the dependency requirements to >=1.2.0 for zc.buildout and
  zc.recipe.egg because relative paths are added in these releases.
- Added missing release date for the previous release (0.10.0).

===================
0.10.0 (2009/09/16)
===================

Removed support for creating a logrotate script for the access.log because it
is not possible to reopen the log with ZDaemons ``reopen_transacript``. Note
however that is is possible to declare ``when`` and ``interval`` in a logfile
section to rotate logfiles internally.


==================
0.9.0 (2009/07/21)
==================

Updated tests to work with latest package versions.

==================
0.8.0 (2009/04/03)
==================

Added the "newest=false" option in the SetUp to prevent upgrade during tests

Added support for creating logrotate scripts when using a deployment recipe.

==================
0.7.0 (2008/02/01)
==================

Use the deployment name option (as provided by zc.recipe.deployment
0.6.0 and later) if present when generating instance file names.

You can now specify an instance name option that overrides the part
name for generated files.

==================
0.6.1 (2007/12/17)
==================

Fixed bug: The zope.conf site-definition option could not be overridden.

==================
0.6.0 (2007/11/03)
==================

Final release with Windows support.

==================
0.6b1 (2007/08/21)
==================

Windows support was added.

==================
0.5.5 (2007/07/26)
==================

Now debugzope takes the servers key of the application into account.

==================
0.5.3 (2007/07/14)
==================

Created another recipe called 'application' that installs Zope 3
solely from eggs.  The 'app' recipe is just an extension that also
supports Zope 3 from checkout or tarball.

==================
0.5.2 (2007/06/21)
==================

Use ZConfig's schema-free configuration parsing gain support for
%import.

==================
0.5.1 (2007/05/22)
==================

Support repeated keys in ZConfig sections.

==================
0.5.0 (2007/03/21)
==================

Support building Zope 3 application solely from eggs.

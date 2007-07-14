**************************************
Zope3 Application and Instance Recipes
**************************************

Recipes for creating Zope 3 instances with distinguishing features:

- Don't use a skeleton

- Separates application and instance definition

- Don't support package-includes

Unfortunately, no Windows support at this time.

.. contents::

Releases
********

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

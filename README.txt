**************************************
Zope3 Application and Instance Recipes
**************************************

Recipes for creating Zope 3 instances with distinguishing features:

- Don't use a skeleton

- Separates application and instance definition

- Don't support package-includes

Unfortunately, partial Windows support at this time. It works but it's alpha.

.. contents::


Trunk
*****

Added windows support. Included a custom ZDCmd and a suprocess wrapper 
in winctl.py. Now the basic commands will also work on a windows box.


Releases
********

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

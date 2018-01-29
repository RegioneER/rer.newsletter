==============
rer.newsletter
==============

.. image::https://travis-ci.org/PloneGov-IT/rer.newsletter.svg?branch=master
    :target: https://travis-ci.org/PloneGov-IT/rer.newsletter

This product allows the management of a newsletter.

Features
--------

- Add two content-types:
  - Channel
  - Message
- Allows complete management of user that subscribe to newsletter
- Allows to substitute the engine that manage how newsletter works.
  For example if you want to use a mailman server, you can rewrite the utility follow
  methods declared in the utility interface.


Example
-------------

Utility declaration::

    <utility
      provides=".channel.IChannelUtility"
      factory=".base.BaseHandler" />

and creates a class that implement utility interface::

    @implementer(IChannelUtility)
    class BaseHandler(object):
        """ utility class to send channel email with mailer of plone """


Installation
------------

Install rer.newsletter by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rer.newsletter


and then running ``bin/buildout``


Dependencies
------------

This product has been tested on Plone 5.1

Credits
-------

Developed with the support of `Regione Emilia Romagna`__;

Regione Emilia Romagna supports the `PloneGov initiative`__.

__ http://www.regione.emilia-romagna.it/
__ http://www.plonegov.it/


License
-------

The project is licensed under the GPLv2.

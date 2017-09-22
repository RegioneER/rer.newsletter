.. This README is meant for consumption by humans and pypi. Pypi can render rst files so please do not use Sphinx features.
   If you want to learn more about writing documentation, please check out: http://docs.plone.org/about/documentation_styleguide.html
   This text does not appear on pypi or github. It is a comment.

==============
rer.newsletter
==============

Tell me what your product does

Features
--------

- Can be bullet points


Examples
--------

This add-on can be seen in action at the following sites:
- Is there a page on the internet where everybody can see the features?

::

    >>> from mailmanclient import Client
    >>> client = Client('http://localhost:9001/3.1', 'restadmin', 'restpass')
    >>> domain = client.create_domain('example.org')
    >>> list = domain.create_list('newsletter')
    >>> list
    <List "newsletter@example.org">
    >>> client.get_list("newsletter@example.org")
    <List "newsletter@example.org">


Documentation
-------------


Translations
------------

This product has been translated into

- Klingon (thanks, K'Plai)


Installation
------------

Install rer.newsletter by adding it to your buildout::

    [buildout]

    ...

    eggs =
        rer.newsletter


and then running ``bin/buildout``


Contribute
----------

- Issue Tracker: https://github.com/collective/rer.newsletter/issues
- Source Code: https://github.com/collective/rer.newsletter
- Documentation: https://docs.plone.org/foo/bar


Support
-------

If you are having issues, please let us know.
We have a mailing list located at: project@example.com


License
-------

The project is licensed under the GPLv2.

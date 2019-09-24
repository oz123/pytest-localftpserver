PyTest FTP Server
=================


.. image:: https://img.shields.io/pypi/v/pytest_localftpserver.svg
        :target:  https://pypi.org/project/pytest-localftpserver/

.. image:: https://img.shields.io/pypi/pyversions/pytest_localftpserver.svg
    :target: https://pypi.org/project/pytest/

.. image:: https://api.travis-ci.org/oz123/pytest-localftpserver.svg?branch=master
        :target: https://travis-ci.org/oz123/pytest-localftpserver

.. image:: https://ci.appveyor.com/api/projects/status/github/oz123/pytest-localftpserver?svg=true
        :target: https://ci.appveyor.com/project/oz123/pytest-localftpserver/branch/master

.. image:: https://readthedocs.org/projects/pytest-localftpserver/badge/?version=latest
        :target: https://pytest-localftpserver.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/oz123/pytest-localftpserver/shield.svg
        :target: https://pyup.io/repos/github/oz123/pytest-localftpserver/
        :alt: Updates

.. image:: https://coveralls.io/repos/github/oz123/pytest-localftpserver/badge.svg
        :target: https://coveralls.io/github/oz123/pytest-localftpserver
        :alt: Coverage


A PyTest plugin which provides an FTP fixture for your tests


* Free software: MIT license
* Documentation: https://pytest-localftpserver.readthedocs.io/en/latest/index.html

Attention!
==========

As of version ``1.0.0`` the support for python 2.7 and 3.4 was dropped.
If you need to support those versions you should pin the version to ``0.6.0``,
i.e. add the following lines to your "requirements_dev.txt"::

        # pytest_localftpserver==0.6.0
        https://github.com/oz123/pytest-localftpserver/archive/v0.6.0.zip


Usage Quickstart:
=================

This Plugin provides the fixtures ``ftpserver`` and ``ftpserver_TLS``,
which are threaded instances of a FTP server, with which you can upload files and test FTP
functionality. It can be configured using the following environment variables:

=====================   =====================================================================
Environment variable    Usage
=====================   =====================================================================
``FTP_USER``            Username of the registered user.
``FTP_PASS``            Password of the registered user.
``FTP_PORT``            Port for the normal ftp server to run on.
``FTP_HOME``            Home folder of the registered user.
``FTP_FIXTURE_SCOPE``   Scope/lifetime of the fixture.
``FTP_PORT_TLS``        Port for the TLS ftp server to run on.
``FTP_HOME_TLS``        Home folder of the registered user, used by the TLS ftp server.
``FTP_CERTFILE``        Certificate to be used by the TLS ftp server.
=====================   =====================================================================


See the `tests directory <https://github.com/oz123/pytest-localftpserver/tree/master/tests>`_
or the
`documentation <https://pytest-localftpserver.readthedocs.io/en/latest/usage.html>`_
for examples.

You can either set environment variables on a system level or use tools such as
`pytest-env <https://pypi.org/project/pytest-env/>`_ or
`tox <https://pypi.org/project/tox/>`_, to change the default settings of this plugin.
Sample config for pytest-cov::

    $ cat pytest.ini
    [pytest]
    env =
        FTP_USER=benz
        FTP_PASS=erni1
        FTP_HOME = /home/ftp_test
        FTP_PORT=31175
        FTP_FIXTURE_SCOPE=function
        # only affects ftpserver_TLS
        FTP_PORT_TLS = 31176
        FTP_HOME_TLS = /home/ftp_test_TLS
        FTP_CERTFILE = ./tests/test_keycert.pem


Sample config for Tox::

    $ cat tox.ini
    [tox]
    envlist = py{27,34,35,36,37}

    [testenv]
    setenv =
        FTP_USER=benz
        FTP_PASS=erni1
        FTP_HOME = {envtmpdir}
        FTP_PORT=31175
        FTP_FIXTURE_SCOPE=function
        # only affects ftpserver_TLS
        FTP_PORT_TLS = 31176
        FTP_HOME_TLS = /home/ftp_test_TLS
        FTP_CERTFILE = {toxinidir}/tests/test_keycert.pem
    commands =
        py.test tests

Credits
=======

This package was inspired by,  https://pypi.org/project/pytest-localserver/
made by Sebastian Rahlf, which lacks an FTP server.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/cookiecutter/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


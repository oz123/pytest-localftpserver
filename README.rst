=================
PyTest FTP Server
=================


.. image:: https://img.shields.io/pypi/v/pytest_localftpserver.svg
        :target: https://pypi.python.org/pypi/pytest_localftpserver

.. image:: https://img.shields.io/pypi/pyversions/pytest_localftpserver.svg
    :target: https://pypi.org/project/pytest/

.. image:: https://travis-ci.org/oz123/pytest-localftpserver.svg?branch=master
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


Usage Quickstart:
=================

  ``ftpserver``
  provides a threaded FTP server where you can upload files and test FTP
  functionality. It has the following attributes:

  * ``ftp_port`` - the server port as integer
  * ``anon_root`` - the root of anonymous user
  * ``ftp_home`` - the root of authenticated user


See the tests directory or the documentation for examples.

You need `pytest-env <https://pypi.org/project/pytest-env/>`_  or
`tox <https://pypi.org/project/tox/>`_
to change the default settings of this plugin.
Sample config for pytest-cov::

    $ cat pytest.ini
    [pytest]
    env =
        FTP_PORT=31175
        FTP_USER=benz
        FTP_PASS=erni1


Sample config for Tox::

    $ cat tox.ini
    [tox]
    envlist = py{27,34,35,36}, flake8

    [testenv]
    setenv =
        FTP_USER = benz
        FTP_PASS = erni1
        FTP_HOME = {envtmpdir}
        FTP_PORT = 31175
    commands =
        py.test tests

Credits
=======

This package was inspired by, https://pypi.python.org/pypi/pytest-localserver/
made by Sebastian Rahlf, which lacks an FTP server.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


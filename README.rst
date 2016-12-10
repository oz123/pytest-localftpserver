===============================
PyTest FTP Server
===============================


.. image:: https://img.shields.io/pypi/v/pytest_localftpserver.svg
        :target: https://pypi.python.org/pypi/pytest_localftpserver

.. image:: https://img.shields.io/travis/oz123/pytest_localftpserver.svg
        :target: https://travis-ci.org/oz123/pytest_localftpserver

.. image:: https://readthedocs.org/projects/pytest-ftp-server/badge/?version=latest
        :target: https://pytest-ftp-server.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/oz123/pytest_localftpserver/shield.svg
     :target: https://pyup.io/repos/github/oz123/pytest_localftpserver/
     :alt: Updates


A PyTest plugin which provides an FTP fixture for your tests


* Free software: MIT license
* Documentation: https://pytest-ftp-server.readthedocs.io.


Usage:
------

``ftpserver``
  provides a threaded FTP server where you can upload files and test FTP
  functionality. It has the following attributes:

  * ``ftp_port`` - the server port as integer
  * ``anon_root`` - the root of anonymous user
  * ``ftp_home`` - the root of authenticated user


See the tests directory for examples.



Credits
---------

This package was inspired by, https://pypi.python.org/pypi/pytest-localserver/
made by Sebastian Rahlf, which lacks an FTP server.

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage


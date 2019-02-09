#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import pytest

from .servers import USE_PROCESS

if USE_PROCESS:
    from .servers import ProcessFTPServer as FTPServer
else:
    from .servers import ThreadFTPServer as FTPServer

# from .servers import ProcessFTPServer as FTPServer

# uncomment the next line to log _option_validator for debugging
# import logging
# logging.basicConfig(filename='option_validator.log', level=logging.INFO)


@pytest.fixture(scope="module")
def ftpserver(request):
    """The returned ``ftpsever`` provides a threaded instance of
    ``pyftpdlib.servers.FTPServer`` running on localhost.

    For details on the usage and configuration  check out the docs at:
    https://pytest-localftpserver.readthedocs.io/en/latest/usage.html

    Yields
    ------
    ftpserver: BaseMPFTPServer
        The type of `ftpserver` isn't actually `BaseMPFTPServer`,
        but a subclass with `threading.Thread` or `multiprocessing.Process`
        depending on the OS. But for autocomplete sake and since
        `BaseMPFTPServer` holds all functionality, let's pretend that it is
        `BaseMPFTPServer`.
    """
    server = FTPServer()
    # This is a must in order to clear used sockets
    server.start()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(scope="module")
def ftpserver_TLS(request):
    """The returned ``ftpsever_TSL`` provides a threaded instance of
    ``pyftpdlib.servers.FTPServer`` using TSL and running on localhost.

    For details on the usage and configuration check out the docs at:
    https://pytest-localftpserver.readthedocs.io/en/latest/usage.html

    Yields
    ------
    ftpserver: BaseMPFTPServer
        The type of `ftpsever_TSL` isn't actually `BaseMPFTPServer`,
        but a subclass with `threading.Thread` or `multiprocessing.Process`
        depending on the OS. But for autocomplete sake and since
        `BaseMPFTPServer` holds all functionality, let's pretend that it is
        `BaseMPFTPServer`.
    """
    server = FTPServer(use_TLS=True)
    # This is a must in order to clear used sockets
    server.start()
    request.addfinalizer(server.stop)
    return server

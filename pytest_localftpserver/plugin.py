#!/usr/bin/env python

import pytest

from .servers import PytestLocalFTPServer
from .helper_functions import get_scope

# uncomment the next line to log _option_validator for debugging
# import logging
# logging.basicConfig(filename='option_validator.log', level=logging.INFO)

FIXTURE_SCOPE = get_scope()


@pytest.fixture(scope=FIXTURE_SCOPE)
def ftpserver(request):
    """The returned ``ftpsever`` provides a threaded instance of
    ``pyftpdlib.servers.FTPServer`` running on localhost.

    For details on the usage and configuration  check out the docs at:
    https://pytest-localftpserver.readthedocs.io/en/latest/usage.html

    Yields
    ------
    ftpserver: FunctionalityWrapper
        The type of `ftpserver` isn't actually `FunctionalityWrapper`,
        but a subclass with `threading.Thread` or `multiprocessing.Process`
        depending on the OS. But for autocomplete sake and since
        `FunctionalityWrapper` holds all functionality, let's pretend that it is
        `FunctionalityWrapper`.
    """
    server = PytestLocalFTPServer()
    request.addfinalizer(server.stop)
    return server


@pytest.fixture(scope=FIXTURE_SCOPE)
def ftpserver_TLS(request):
    """The returned ``ftpsever_TSL`` provides a threaded instance of
    ``pyftpdlib.servers.FTPServer`` using TSL and running on localhost.

    For details on the usage and configuration check out the docs at:
    https://pytest-localftpserver.readthedocs.io/en/latest/usage.html

    Yields
    ------
    ftpserver: FunctionalityWrapper
        The type of `ftpsever_TSL` isn't actually `FunctionalityWrapper`,
        but a subclass with `threading.Thread` or `multiprocessing.Process`
        depending on the OS. But for autocomplete sake and since
        `FunctionalityWrapper` holds all functionality, let's pretend that it is
        `FunctionalityWrapper`.
    """
    server = PytestLocalFTPServer(use_TLS=True)
    request.addfinalizer(server.stop)
    return server

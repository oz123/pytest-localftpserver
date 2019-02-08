#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import

import sys

import pytest

from .helper_functions import get_env_dict
if sys.platform.startswith('linux'):
    USE_PROCESS = True
    from .servers import ProcessFTPServer as FTPServer
else:
    USE_PROCESS = False
    from .servers import ThreadFTPServer as FTPServer


# uncomment the next line to log _option_validator for debugging
# import logging
# logging.basicConfig(filename='option_validator.log', level=logging.INFO)


@pytest.fixture(scope="module", autouse=True)
def ftpserver(request):
    """The returned ``ftpsever`` provides a threaded instance of
    ``pyftpdlib.servers.FTPServer`` running on localhost.  It has the following
    attributes:

    * ``ftp_port`` - the server port as integer
    * ``anon_root`` - the root of anonymous user
    * ``ftp_home`` - the root of authenticated user

    If you wish to control the credentials and home for the authenticated user,
    define in the test module the following 3 global variables:

    * ``ftp_username`` - login name (default: fakeusername).
    * ``ftp_password`` - login password (default: qweqweqwe).
    * ``ftp_home`` - the root for the authenticated user.

    Yields
    ------
    ftpserver: BaseMPFTPServer
        The type of `ftpserver` isn't actually `BaseMPFTPServer`,
        but a subclass with `threading.Thread` or `multiprocessing.Process`
        depending on the OS. But for autocomplete sake and since
        `BaseMPFTPServer` holds all functionality, let's pretend that it is
        `BaseMPFTPServer`.
    """
    env_dict = get_env_dict()
    server = FTPServer(**env_dict)
    # This is a must in order to clear used sockets
    server.daemon = True
    server.start()
    yield server
    server.stop()

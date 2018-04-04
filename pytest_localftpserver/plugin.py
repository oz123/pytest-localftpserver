# -*- coding: utf-8 -*-

import multiprocessing
import os
import shutil
import socket
import sys
import tempfile
import threading


from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import pytest

if sys.platform.startswith('linux'):
    USE_PROCESS = True
else:
    USE_PROCESS = False


class SimpleFTPServer(FTPServer):
    """
    Starts a simple FTP server on a random free port.

    https://github.com/Lukasa/requests-ftp/
    """

    def __init__(self, username, password, ftp_home=None, ftp_port=0):
        # Create temp directories for the anonymous and authenticated roots
        self._anon_root = tempfile.mkdtemp()
        if not ftp_home:
            self._ftp_home = tempfile.mkdtemp()
        self.username = username
        self.password = password
        authorizer = DummyAuthorizer()
        authorizer.add_user(self.username, self.password, self.ftp_home,
                            perm='elradfmwM')
        authorizer.add_anonymous(self.anon_root)

        handler = FTPHandler
        handler.authorizer = authorizer
        # Create a socket on any free port
        self._ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ftp_socket.bind(('127.0.0.1', ftp_port))
        self._ftp_port = self._ftp_socket.getsockname()[1]

        # Create a new pyftpdlib server with the socket and handler we've
        # configured
        FTPServer.__init__(self, self._ftp_socket, handler)

    @property
    def anon_root(self):
        """Home directory for the anonymous user"""
        return self._anon_root

    @property
    def ftp_home(self):
        """FTP home for the ftp_user"""
        return self._ftp_home

    @property
    def ftp_port(self):
        return self._ftp_port

    def __del__(self):
        self.stop()

    def stop(self):
        self.close_all()
        for item in ['_anon_root', '_ftp_home']:
            if hasattr(self, item):
                shutil.rmtree(self._anon_root, ignore_errors=True)


class BaseMPFTPServer(object):

    def __init__(self, username, password, ftp_home, ftp_port):

        self._server = SimpleFTPServer(username, password,
                                       ftp_home, ftp_port)

    @property
    def server_port(self):
        return self._server._ftp_port

    @property
    def server_home(self):
        """FTP home for the ftp_user"""
        if hasattr(self._server, "_ftp_home"):
            return self._server._ftp_home
        else:
            return None

    @property
    def anon_root(self):
        return self._server._anon_root

    def stop(self):
        self._server.stop()

    def __del__(self):
        self.stop()


class ThreadFTPServer(BaseMPFTPServer, threading.Thread):

    def __init__(self, username, password, ftp_home, ftp_port, **kwargs):
        # inheriting isn't done via super, since the strict order matters
        threading.Thread.__init__(self, **kwargs)
        BaseMPFTPServer.__init__(self, username, password,
                                 ftp_home, ftp_port)

    def run(self):
        self._server.serve_forever()


class ProcessFTPServer(BaseMPFTPServer, multiprocessing.Process):

    def __init__(self, username, password, ftp_home, ftp_port, **kwargs):
        # inheriting isn't done via super, since the strict order matters
        multiprocessing.Process.__init__(self, **kwargs)
        BaseMPFTPServer.__init__(self, username, password,
                                 ftp_home, ftp_port)

    def run(self):
        self._server.serve_forever()

    def stop(self):
        self._server.stop()
        self.terminate()


@pytest.fixture(scope="session", autouse=True)
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
    """
    # from pytest_localftpserver.plugin import MPFTPServer
    ftp_user = os.getenv("FTP_USER", "fakeusername")
    ftp_password = os.getenv("FTP_PASS", "qweqwe")
    ftp_home = os.getenv("FTP_HOME", "")
    ftp_port = int(os.getenv("FTP_PORT", 0))
    if USE_PROCESS:
        server = ProcessFTPServer(ftp_user, ftp_password, ftp_home, ftp_port)
    else:
        server = ThreadFTPServer(ftp_user, ftp_password, ftp_home, ftp_port)
    # This is a must in order to clear used sockets
    server.daemon = True
    server.start()
    yield server
    if USE_PROCESS:
        server.terminate()


if __name__ == "__main__":
    server = SimpleFTPServer("fakeusername", "qweqwe")
    print("FTPD running on port %d" % server.ftp_port)
    print("Anonymous root: %s" % server.anon_root)
    print("Authenticated root: %s" % server.ftp_home)
    server.serve_forever()

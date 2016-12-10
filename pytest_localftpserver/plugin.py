# -*- coding: utf-8 -*-

import shutil
import socket
import tempfile
import threading


from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

import pytest

class SimpleFTPServer(FTPServer):
    """
    Starts a simple FTP server on a random free port.

    https://github.com/Lukasa/requests-ftp/
    """

    def __init__(self):
        # Create temp directories for the anonymous and authenticated roots
        self._anon_root = tempfile.mkdtemp()
        self._ftp_home = tempfile.mkdtemp()

        authorizer = DummyAuthorizer()
        authorizer.add_user(self.ftp_user, self.ftp_password, self.ftp_home,
                            perm='elradfmwM')
        authorizer.add_anonymous(self.anon_root)

        handler = FTPHandler
        handler.authorizer = authorizer

        # Create a socket on any free port
        self._ftp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._ftp_socket.bind(('127.0.0.1', 0))
        self._ftp_port = self._ftp_socket.getsockname()[1]

        # Create a new pyftpdlib server with the socket and handler we've
        # configured
        FTPServer.__init__(self, self._ftp_socket, handler)

    @property
    def anon_root(self):
        """Home directory for the anonymous user"""
        return self._anon_root

    @property
    def ftp_user(self):
        """User name added for authenticated connections"""
        return 'fakeusername'

    @property
    def ftp_password(self):
        """Password for ftp_user"""
        return 'qweqwe'

    @property
    def ftp_home(self):
        """FTP home for the ftp_user"""
        return self._ftp_home

    @property
    def ftp_port(self):
        """TCP port that the server is listening on"""
        return self._ftp_port

    def __del__(self):
        self.stop()

    def stop(self):
        self.close_all()
        if hasattr(self, '_anon_root'):
            shutil.rmtree(self._anon_root, ignore_errors=True)

        if hasattr(self, '_ftp_home'):
            shutil.rmtree(self._ftp_home, ignore_errors=True)


class ThreadedFTPServer(threading.Thread):

    def __init__(self, **kwargs):
        self._server = SimpleFTPServer()
        self.server_home = self._server.ftp_home
        self.anon_root = self._server.anon_root
        self.server_port = self._server.ftp_port

        super(ThreadedFTPServer, self).__init__(
            name=self.__class__, target=self._server.serve_forever)

    def join(self):
        self._server.stop()

    def stop(self):
        self._server.stop()


@pytest.fixture
def ftpserver(scope="module", autouse=True):
    """The returned ``ftpsever`` provides a threaded instance of
    ``pyftpdlib.servers.FTPServer`` running on localhost.  It has the following
    attributes:

    * ``ftp_port`` - the server port as integer
    * ``anon_root`` - the root of anonymous user
    * ``ftp_home`` - the root of authenticated user
    """
    from pytest_localftpserver.plugin import ThreadedFTPServer
    server = ThreadedFTPServer()
    server.daemon = True
    server.start()
    yield server
    server.join()


if __name__ == "__main__":
    server = SimpleFTPServer()
    print("FTPD running on port %d" % server.ftp_port)
    print("Anonymous root: %s" % server.anon_root)
    print("Authenticated root: %s" % server.ftp_home)
    server.serve_forever()




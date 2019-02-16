from ftplib import FTP
import os
import pytest

from pytest_localftpserver.servers import PytestLocalFTPServer
from .test_pytest_localftpserver import test_ftp_stopped


# uncomment the next line to log _option_validator for debugging
# import logging
# logging.basicConfig(filename='option_validator.log', level=logging.INFO)


@pytest.fixture(scope="function")
def ftpserver_func_scope(request):
    server = PytestLocalFTPServer()
    request.addfinalizer(server.stop)
    return server


def test_shutdown(ftpserver_func_scope):
    assert ftpserver_func_scope.server_port == 31175
    test_ftp_stopped(ftpserver_func_scope)


def test_server_running_again(ftpserver_func_scope):
    local_anon_path = ftpserver_func_scope.get_local_base_path(anon=True)
    local_ftp_home = ftpserver_func_scope.get_local_base_path(anon=False)
    ftp = FTP()
    ftp.connect("localhost", port=ftpserver_func_scope.server_port)
    assert ftpserver_func_scope.server_port == 31175
    # check if all temp folders are recreated
    assert os.path.exists(local_anon_path)
    assert os.path.exists(local_ftp_home)

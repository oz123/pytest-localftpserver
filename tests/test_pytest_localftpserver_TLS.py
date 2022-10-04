#!/usr/bin/env python

"""
test_pytest_localftpserver
----------------------------------

Tests for `pytest_localftpserver` module.
"""

import os

from ftplib import error_perm
import pytest


from .test_pytest_localftpserver import (ftp_login,
                                         check_files_by_ftpclient,
                                         close_client,
                                         FILE_LIST)

from pytest_localftpserver.servers import (SimpleFTPServer,
                                           WrongFixtureError,
                                           DEFAULT_CERTFILE)

from pytest_localftpserver.helper_functions import InvalidCertificateError


def test_is_TLS(ftpserver_TLS):
    assert ftpserver_TLS.uses_TLS is True


@pytest.mark.parametrize("anon",
                         [True, False])
def test_get_login_data(ftpserver_TLS, anon):
    login_dict = ftpserver_TLS.get_login_data(style="dict")
    assert login_dict["host"] == "localhost"
    assert login_dict["port"] == ftpserver_TLS.server_port
    if not anon:
        assert login_dict["user"] == "fakeusername"
        assert login_dict["passwd"] == "qweqwe"
    login_url = ftpserver_TLS.get_login_data(style="url", anon=anon)
    if anon:
        base_url = "ftpes://localhost:"
    else:
        base_url = "ftpes://fakeusername:qweqwe@localhost:"
    assert login_url == base_url + str(ftpserver_TLS.server_port)


def test_file_upload_user(ftpserver_TLS, tmpdir):
    # makes sure to start with clean temp dirs
    ftpserver_TLS.reset_tmp_dirs()
    ftp = ftp_login(ftpserver_TLS, use_TLS=True)
    ftp.cwd("/")
    ftp.mkd("FOO")
    ftp.cwd("FOO")
    filename = "testfile.txt"
    file_path_local = tmpdir.join(filename)
    file_path_local.write("test")
    with open(str(file_path_local), "rb") as f:
        ftp.storbinary("STOR "+filename, f)
    close_client(ftp)

    assert os.path.isdir(os.path.join(ftpserver_TLS.server_home, "FOO"))
    abs_file_path_server = os.path.join(ftpserver_TLS.server_home, "FOO",
                                        filename)
    assert os.path.isfile(abs_file_path_server)
    with open(abs_file_path_server) as f:
        assert f.read() == "test"


def test_file_upload_anon(ftpserver_TLS):
    # anon user has no write privileges
    ftp = ftp_login(ftpserver_TLS, anon=True, use_TLS=True)
    ftp.cwd("/")
    with pytest.raises(error_perm):
        ftp.mkd("FOO")
    close_client(ftp)


@pytest.mark.parametrize("anon",
                         [False, True])
def test_get_file_paths(tmpdir, ftpserver_TLS, anon):
    # makes sure to start with clean temp dirs
    ftpserver_TLS.reset_tmp_dirs()
    base_path = ftpserver_TLS.get_local_base_path(anon=anon)
    files_on_server = []
    for dirs, filename in FILE_LIST:
        dir_path = os.path.abspath(os.path.join(base_path, dirs))
        if dirs != "":
            os.makedirs(dir_path)
        abs_file_path = os.path.join(dir_path, filename)
        file_path = "/".join([dirs, filename]).lstrip("/")
        files_on_server.append(file_path)
        with open(abs_file_path, "a") as f:
            f.write(filename)

    path_iterable = list(ftpserver_TLS.get_file_paths(anon=anon))
    assert len(path_iterable) == len(FILE_LIST)
    # checking the files by rel_path to user home dir
    # and native ftp client
    check_files_by_ftpclient(ftpserver_TLS,
                             tmpdir,
                             files_on_server,
                             path_iterable,
                             anon,
                             use_TLS=True)


@pytest.mark.parametrize("style, read_mode", [
    ("path", "r"),
    ("content", "r"),
    ("content", "rb")
])
def test_ftpserver_TLS_get_cert(ftpserver_TLS, style, read_mode):
    result = ftpserver_TLS.get_cert(style=style, read_mode=read_mode)
    if style == "path":
        assert result == DEFAULT_CERTFILE
    else:
        with open(DEFAULT_CERTFILE, read_mode) as certfile:
            assert result == certfile.read()


def test_ftpserver_get_cert_exceptions(ftpserver, ftpserver_TLS):
    with pytest.raises(
            WrongFixtureError,
            match=r"The fixture ftpserver isn't using TLS, and thus"
                  r"has no certificate. Use ftpserver_TLS instead."):
        ftpserver.get_cert()

    # type errors
    with pytest.raises(
            TypeError,
            match="The Argument `style` needs to be of type "
                  "``str``, the type given type was ``bool``."):
        ftpserver.get_cert(style=True)

    with pytest.raises(
            TypeError,
            match="The Argument `read_mode` needs to be of type "
                  "``str``, the type given type was ``bool``."):
        ftpserver.get_cert(read_mode=True)

    # value errors
    with pytest.raises(
            ValueError,
            match="The Argument `style` needs to be of value "
                  "'path' or 'content', the given value was 'dict'."):
        list(ftpserver.get_cert(style="dict"))

    with pytest.raises(
            ValueError,
            match="The Argument `read_mode` needs to be of value "
                  "'r' or 'rb', the given value was 'invalid_option'."):
        list(ftpserver.get_cert(read_mode="invalid_option"))


def test_wrong_cert_exception():
    wrong_cert = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              "not_a_valid_cert.pem"))
    with pytest.raises(InvalidCertificateError):
        SimpleFTPServer(use_TLS=True, certfile=wrong_cert)

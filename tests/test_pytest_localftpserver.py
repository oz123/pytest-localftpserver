#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_localftpserver
----------------------------------

Tests for `pytest_localftpserver` module.
"""

import os
from ftplib import FTP

import pytest
from pytest_localftpserver import plugin


def test_ftpserver(ftpserver):
    assert isinstance(ftpserver, plugin.ThreadedFTPServer)
    assert ftpserver.server_home
    assert ftpserver.server_port


def test_ftp_stopped(ftpserver):
    ftpserver.stop()
    ftp = FTP()
    with pytest.raises(ConnectionRefusedError):
        ftp.connect("localhost", port=ftpserver.server_port)


def test_file_upload(ftpserver):
    ftp = FTP()
    ftp.connect("localhost", port=ftpserver.server_port)
    ftp.login("fakeusername", "qweqwe")
    ftp.cwd("/")
    ftp.mkd("FOO")
    ftp.quit()

    assert os.path.exists(os.path.join(ftpserver.server_home, "FOO"))


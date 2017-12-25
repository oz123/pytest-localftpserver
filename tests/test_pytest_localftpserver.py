#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest_localftpserver
----------------------------------

Tests for `pytest_localftpserver` module.
"""

from __future__ import print_function

import os
import socket
import sys
from ftplib import FTP

import pytest

from pytest_localftpserver import plugin


if sys.version_info[0] == 3:
    PYTHON3 = True
else:
    PYTHON3 = False


def test_ftpserver(ftpserver):
    assert isinstance(ftpserver, plugin.MPFTPServer)


def test_file_upload(ftpserver):
    ftp = FTP()
    ftp.connect("localhost", port=ftpserver.server_port)
    ftp.login("fakeusername", "qweqwe")
    ftp.cwd("/")
    ftp.mkd("FOO")
    ftp.quit()

    assert os.path.exists(os.path.join(ftpserver.server_home, "FOO"))


def test_ftp_stopped(ftpserver):
    ftpserver.stop()
    ftp = FTP()
    if PYTHON3:
        with pytest.raises(OSError):
            ftp.connect("localhost", port=ftpserver.server_port)
    else:
        #  python2.7 raises an different error than python3.3>
        with pytest.raises(socket.error):
            ftp.connect("localhost", port=ftpserver.server_port)

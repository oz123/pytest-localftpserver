#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from pytest_localftpserver.helper_functions import get_env_dict


def test_get_env_dict():
    result_dict = {}
    result_dict["username"] = "benz"
    result_dict["password"] = "erni1"
    result_dict["ftp_home"] = os.getenv("FTP_HOME")
    result_dict["ftp_port"] = 31175
    result_dict["ftp_port_TLS"] = 31176
    result_dict["certfile"] = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                           "test_keycert.pem"))
    env_dict = get_env_dict()
    assert env_dict == result_dict


def test_customize_server(ftpserver):
    assert ftpserver.server_port == 31175
    assert ftpserver.username == "benz"
    assert ftpserver.password == "erni1"
    assert ftpserver.server_home == os.getenv("FTP_HOME")


def test_customize_server_TLS(ftpserver_TLS):
    assert ftpserver_TLS.server_port == 31176
    assert ftpserver_TLS.username == "benz"
    assert ftpserver_TLS.password == "erni1"
    assert ftpserver_TLS.server_home == os.getenv("FTP_HOME")

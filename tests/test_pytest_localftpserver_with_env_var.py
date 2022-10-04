#!/usr/bin/env python
from ftplib import FTP
import os

import pytest
from pytest_localftpserver.helper_functions import get_env_dict

from .test_pytest_localftpserver import run_ftp_stopped_test


# uncomment the next line to log _option_validator for debugging
# import logging
# logging.basicConfig(filename='option_validator.log', level=logging.INFO)


@pytest.mark.parametrize("use_TLS", [True, False])
def test_get_env_dict(use_TLS):
    result_dict = {}
    result_dict["username"] = "benz"
    result_dict["password"] = "erni1"
    result_dict["certfile"] = os.path.abspath(
            os.path.join(os.path.dirname(__file__),
                         "test_keycert.pem"))
    if use_TLS:
        result_dict["ftp_home"] = os.getenv("FTP_HOME_TLS", "")
        result_dict["ftp_port"] = 31176
    else:
        result_dict["ftp_home"] = os.getenv("FTP_HOME", "")
        result_dict["ftp_port"] = 31175

    env_dict = get_env_dict(use_TLS=use_TLS)
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
    assert ftpserver_TLS.server_home == os.getenv("FTP_HOME_TLS")


# FUNCTION SCOPE TESTS


def test_shutdown(ftpserver):
    assert ftpserver.server_port == 31175
    local_anon_path = ftpserver.get_local_base_path(anon=True)
    local_ftp_home = ftpserver.get_local_base_path(anon=False)
    run_ftp_stopped_test(ftpserver)
    # check if all anon home folders got cleared properly
    assert not os.path.exists(local_anon_path)
    # since home was provided via config it shouldn't be deleted
    assert os.path.exists(local_ftp_home)


def test_server_running_again(ftpserver):
    local_anon_path = ftpserver.get_local_base_path(anon=True)
    local_ftp_home = ftpserver.get_local_base_path(anon=False)
    ftp = FTP()
    ftp.connect("localhost", port=ftpserver.server_port)
    assert ftpserver.server_port == 31175
    # check if all temp folders are recreated
    assert os.path.exists(local_anon_path)
    assert os.path.exists(local_ftp_home)

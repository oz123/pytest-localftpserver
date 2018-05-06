#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

def test_set_server_home(ftpserver):
    assert ftpserver.server_port == 31175
    assert ftpserver.username ==  "benz"
    assert ftpserver.password ==  "erni1"
    assert ftpserver.server_home ==  os.getenv("FTP_HOME")



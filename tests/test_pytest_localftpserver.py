#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_pytest-localftpserver
----------------------------------

Tests for `pytest-localftpserver` module.
"""

import pytest


from pytest_localftpserver import pytest_localftpserver


@pytest.fixture
def response():
    """Sample pytest fixture.
    See more at: http://doc.pytest.org/en/latest/fixture.html
    """
    # import requests
    # return requests.get('https://github.com/audreyr/cookiecutter-pypackage')


def test_content(response):
    """Sample pytest test function with the pytest fixture as an argument.
    """
    # from bs4 import BeautifulSoup
    # assert 'GitHub' in BeautifulSoup(response.content).title.string

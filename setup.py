#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pyftpdlib',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pytest_localftpserver',
    version='0.1.0',
    description="A PyTest plugin which provides an FTP fixture for your tests",
    long_description=readme + '\n\n' + history,
    author="Oz Tiram",
    author_email='oz.tiram@gmail.com',
    url='https://github.com/oz123/pytest_localftpserver',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pytest_ftpserver',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Framework :: Pytest",
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
                  'pytest11': ['ftpstub = pytest_localftpserver.plugin']
    },
)

#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'pyftpdlib>=1.2.0',
    'PyOpenSSL',
    'pytest'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='pytest_localftpserver',
    version='1.1.3',
    description="A PyTest plugin which provides an FTP fixture for your tests",
    long_description=readme + '\n\n' + history,
    long_description_content_type="text/x-rst",
    author="Oz Tiram",
    author_email='oz.tiram@gmail.com',
    url='https://github.com/oz123/pytest-localftpserver',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='pytest_localftpserver pytest fixture ftp server local',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        "Framework :: Pytest",
        'Topic :: Software Development :: Testing',
        "Topic :: Software Development :: Testing :: Mocking"
    ],
    test_suite='tests',
    tests_require=test_requirements,
    entry_points={
                  'pytest11': ['localftpserver = pytest_localftpserver.plugin']
    },
)

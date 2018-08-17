=====
Usage
=====

After installing `pytest_localftpserver` the fixture ``ftpserver`` is available for
your pytest test functions. Note that you can't use fixtures outside of functions and
need to pass them as arguments.

Basic usage
-----------

A basic example of using `pytest_localftpserver` would be, if you wanted to test code,
which uploads a file to a FTP-server.

.. code-block:: python

    import os


    def test_your_code_to_upload_files(ftpserver):
        your_code_to_upload_files(host="localhost",
                                  port=ftpserver.server_port,
                                  username=ftpserver.username,
                                  password=ftpserver.password,
                                  files=["testfile.txt"])

        uploaded_file_path = os.path.join(ftpserver.server_home, "testfile.txt")
        with open("testfile.txt") as original, open(uploaded_file_path) as uploaded:
            assert original.read() == uploaded.read()

.. note::  Like most public FTP-servers `pytest_localftpserver` doesn't allow the anonymous
           user to upload files. The anonymous user is only allowed to browse the folder structure
           and download files. If you want to upload files you need to use the registered user,
           with its password.

An other common use case would be retrieving a file from a FTP-server.

.. code-block:: python

    import os
    from shutil import copyfile


    def test_your_code_retrieving_files(ftpserver):
        dest_path = os.path.join(ftpserver.anon_root, "testfile.txt")
        copyfile("testfile.txt", dest_path)
        your_code_retrieving_files(host="localhost",
                                   port=ftpserver.server_port
                                   file_paths=[{"remote": "testfile.txt",
                                                "local": "testfile_downloaded.txt"
                                                }])
        with open("testfile.txt") as original, open("testfile_downloaded.txt") as downloaded:
            assert original.read() == downloaded.read()


High-Level Interface
--------------------

To allow you a faster and more comfortable handling of common ftp tasks a high-level
interface was implemented. Most of the following methods have the keyword ``anon``, which
allows to switch between the registered (`anon=False`) and the anonymous (`anon=True`) user.
For more information on how those methods work, take a look at the `API Documentation <api_doc.html>`_ .

.. note::  The following examples aren't working code, since the aren't called from
           within a function, which means that the ``ftpserver`` fixture isn't available.
           They are thought to be a quick overview of the available functionality and
           its output.

Getting login credentials
^^^^^^^^^^^^^^^^^^^^^^^^^

To quickly get all needed login data you can use ``get_login_data``, which will either return
a dict or an url to log into the ftp::

    >>> ftpserver.get_login_data()
    {"host": "localhost", "port": 8888, "user": "fakeusername", "passwd": "qweqwe"}

    >>> ftpserver.get_login_data(style="url", anon=False)
    ftp://fakeusername:qweqwe@localhost:8888

    >>> ftpserver.get_login_data(style="url", anon=True)
    ftp://localhost:8888


Populating the FTP server with files and folders
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To test ftp download capabilities of your code, you might want to populate the files on the server.
To "upload" files to the server you can use the method ``put_files``::


    >>> ftpserver.put_files("test_folder/test_file", style="rel_path", anon=False)
    ["test_file"]

    >>> ftpserver.put_files("test_folder/test_file", style="url", anon=False)
    ["ftp://fakeusername:qweqwe@localhost:8888/test_file"]

    >>> ftpserver.put_files("test_folder/test_file", style="url", anon=True)
    ["ftp://localhost:8888/test_file"]

    >>> ftpserver.put_files({"src": "test_folder/test_file",
    ...                      "dest": "remote_folder/uploaded_file"},
    ...                     style="url", anon=True)
    ["ftp://localhost:8888/remote_folder/uploaded_file"]

    >>> ftpserver.put_files("test_folder/test_file", return_content=True)
    [{"path": "test_file", "content": "some text in test_file"}]

    >>> ftpserver.put_files("test_file.zip", return_content=True, read_mode="rb")
    [{"path": "test_file.zip", "content": b'PK\\x03\\x04\\x14\\x00\\x00...'}]

    >>> ftpserver.put_files("test_file", return_paths="new")
    UserWarning: test_file does already exist and won't be overwritten.
        Set `overwrite` to True to overwrite it anyway.
    []

    >>> ftpserver.put_files("test_file", return_paths="new", overwrite=True)
    ["test_file"]

    >>> ftpserver.put_files("test_file3", return_paths="all")
    ["test_file", "remote_folder/uploaded_file", "test_file.zip"]

Resetting files on the server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Since ``ftpserver`` is a module scope fixture, you might want to make sure that uploaded files
get deleted after/before a test. This can be done by using the method ``reset_tmp_dirs``.

`filesystem before`:

.. code:: bash

    +---server_home
    |   +---test_file1
    |   +---test_folder
    |       +---test_file2
    |
    +---anon_root
        +---test_file3
        +---test_folder
            +---test_file4

.. code:: python

    >>> ftpserver.reset_tmp_dirs()

`filesystem after`:

.. code:: bash

  +---server_home
  |
  +---anon_root

Gaining information on which files are on the server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you want to know which files are on the server, i.e. if you want to know if your
file upload functionality is working, you can use the ``get_file_paths`` method, which will
yield the paths to all files on the server.

.. code:: bash

      filesystem
      +---server_home
      |   +---test_file1
      |   +---test_folder
      |       +---test_file2
      |
      +---anon_root
          +---test_file3
          +---test_folder
              +---test_file4

.. code:: python

    >>> list(ftpserver.get_file_paths(style="rel_path", anon=False))
    ["test_file1", "test_folder/test_file2"]

    >>> list(ftpserver.get_file_paths(style="rel_path", anon=True))
    ["test_file3", "test_folder/test_file4"]

Gaining information about the content of files on the server
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If you are interested in the content of a specific file, multiple files or all files,
i.e. to verify that your file upload functionality did work properly, you can use the
``get_file_contents`` method.

.. code:: bash

  filesystem
  +---server_home
      +---test_file1.txt
      +---test_folder
          +---test_file2.zip


.. code:: python

    >>> list(ftpserver.get_file_contents())
    [{"path": "test_file1.txt", "content": "test text"},
     {"path": "test_folder/test_file2.txt", "content": "test text2"}]

    >>> list(ftpserver.get_file_contents("test_file1.txt"))
    [{"path": "test_file1.txt", "content": "test text"}]

    >>> list(ftpserver.get_file_contents("test_file1.txt", style="url"))
    [{"path": "ftp://fakeusername:qweqwe@localhost:8888/test_file1.txt",
      "content": "test text"}]

    >>> list(ftpserver.get_file_contents(["test_file1.txt", "test_folder/test_file2.zip"],
    ...                                  read_mode="rb"))
    [{"path": "test_file1.txt", "content": b"test text"},
     {"path": "test_folder/test_file2.zip", "content": b'PK\\x03\\x04\\x14\\x00\\x00...'}]



Configuration
-------------

To configure custom values for for the username, the users password, the ftp port and/or
the location of the users home folder on the local storage, you need to set the environment
variables ``FTP_USER``, ``FTP_PASS``, ``FTP_PORT`` and ``FTP_HOME``.
You can either do that on a system level or use tools such as
`pytest-env <https://pypi.org/project/pytest-env/>`_ or
`tox <https://pypi.org/project/tox/>`_

Configuration with pytest-env
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The configuration of pytest-env is done in the ``pytest.ini`` file.
The following example configuration will use the username benz, the password erni1
and the ftp port 31175::

    $ cat pytest.ini
    [pytest]
    env =
        FTP_PORT=31175
        FTP_USER=benz
        FTP_PASS=erni1


Configuration with Tox
^^^^^^^^^^^^^^^^^^^^^^

The configuration of tox is done in the ``tox.ini`` file.
The following example configuration will run the tests in the folder ``tests`` on
python 2.7, 3.4, 3.5 and 3.6 and use the username benz, the password erni1,
the tempfolder of of each virtual environment the tests are run in and the ftp port 31175::

    $ cat tox.ini
    [tox]
    envlist = py{27,34,35,36}

    [testenv]
    setenv =
        FTP_USER = benz
        FTP_PASS = erni1
        FTP_HOME = {envtmpdir}
        FTP_PORT = 31175
    commands =
        py.test tests


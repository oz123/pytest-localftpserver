#!/usr/bin/env python

"""
test_pytest_localftpserver
----------------------------------

Tests for `pytest_localftpserver` module.
"""

from ftplib import FTP, FTP_TLS, error_perm
import logging
import os
import urllib.request

import pytest

from pytest_localftpserver.plugin import PytestLocalFTPServer
from pytest_localftpserver.servers import USE_PROCESS
from pytest_localftpserver.helper_functions import DEFAULT_CERTFILE


from ssl import SSLContext, PROTOCOL_TLS_CLIENT, TLSVersion

# HELPER FUNCTIONS


FILE_LIST = [
    ("", "testfile1"),
    ("testdir", "testfile2"),
    ("testdir/nested", "testfile3"),
]


def ftp_login(ftp_fixture, anon=False, use_TLS=False):
    """
    Convenience function to reduce code overhead.
    Logs in the FTP client and returns the ftplib.FTP instance

    Parameters
    ----------
    ftp_fixture: FTPServer

    anon: bool
            True:
                Use anon_root as basepath

            False:
                Use server_home as basepath

    Returns
    -------
    ftp: ftplib.FTP
        logged in FTP client

    """
    if use_TLS:
        ssl_context = SSLContext(PROTOCOL_TLS_CLIENT)
        ssl_context.minimum_version = TLSVersion.TLSv1_2
        ssl_context.maximum_version = TLSVersion.TLSv1_3
        ssl_context.load_cert_chain(certfile=DEFAULT_CERTFILE)
        ftp = FTP_TLS(context=ssl_context)
    else:
        ftp = FTP()
    login_dict = ftp_fixture.get_login_data()
    ftp.connect(login_dict["host"], login_dict["port"])
    if anon:
        ftp.login()
    else:
        ftp.login(login_dict["user"], login_dict["passwd"])
    if use_TLS:
        ftp.prot_p()
    return ftp


def close_client(session):
    # taken from https://github.com/giampaolo/pyftpdlib/ \
    #         blob/master/pyftpdlib/test/__init__.py
    """Closes a ftplib.FTP client session."""
    try:
        if session.sock is not None:
            try:
                resp = session.quit()
            except Exception:
                pass
            else:
                # ...just to make sure the server isn't replying to some
                # pending command.
                assert resp.startswith("221"), resp
    finally:
        session.close()


def check_files_by_ftpclient(
    ftp_fixture,
    tmpdir,
    files_on_server,
    path_iterable,
    anon=False,
    use_TLS=False
):
    """
    Convenience function to reduce code overhead.
    Downloading files with a native ftp client and checking their content.

    Parameters
    ----------
    ftp_fixture: FTPServer

    anon: bool
            True:
                Use anon_root as basepath

            False:
                Use server_home as basepath

    Returns
    -------
    ftp: ftplib.FTP
        logged in FTP client
    """
    # checking the files by rel_path to user home dir
    # and native ftp client
    if anon:
        base_path = ftp_fixture.anon_root
    else:
        base_path = ftp_fixture.server_home
    ftp = ftp_login(ftp_fixture, anon=anon, use_TLS=use_TLS)
    download_dir = tmpdir.mkdir("download_rel_path")
    for file_path in path_iterable:
        abs_file_path = os.path.abspath(os.path.join(base_path, file_path))
        assert os.path.isfile(abs_file_path)
        assert file_path in files_on_server
        dirs, filename = os.path.split(file_path)
        if dirs != "":
            download_file = download_dir.mkdir(dirs).join(filename)
        else:
            download_file = download_dir.join(filename)
        with open(str(download_file), "wb") as f:
            ftp.retrbinary("RETR " + file_path, f.write)
        with open(str(download_file)) as f:
            assert f.read() == filename
    close_client(ftp)
    download_dir.remove()


def check_files_by_urls(tmpdir, base_url, url_iterable):
    """
    Convenience function to reduce code overhead.
    Downloading files by urls and checking their content.

    Parameters
    ----------
    tmpdir: Path
        Tempdir to download files to
    base_url: str
        Base ur to the ftp server to mimic its folder structure
    url_iterable: iterable of urls
        Contains urls to check
    """
    # checking files by url
    for url in url_iterable:
        _, filename = os.path.split(os.path.relpath(url, base_url))
        with urllib.request.urlopen(url) as response:
            assert response.read() == filename.encode()


def check_get_file_contents(
    tmpdir,
    path_list,
    iterable_len,
    files_on_server,
    style,
    base_url,
    read_mode
):
    """
    Convenience function to reduce code overhead.
    Compares expected file content with actual file content.

    Parameters
    ----------
    tmpdir: Path
        Tempdir to download files to
    path_list: list
        List of filepaths to check
    iterable_len: int
        Len of path_list
    files_on_server: list
        List of relative file path on the server
    style: "rel_path", "url"
        Mode in which filepaths on the ftpserver are given
    base_url: str
        Base ur to the ftp server to mimic its folder structure
    read_mode: "r", "rb"
        Mode in which files should be read

    Returns
    -------

    """
    assert len(path_list) == iterable_len
    for content_dict in path_list:
        assert isinstance(content_dict, dict)
        assert "path" in content_dict and "content" in content_dict
        file_content = os.path.split(content_dict["path"])[1]
        if read_mode == "rb":
            file_content = file_content.encode()
        if style == "rel_path":
            assert content_dict["path"] in files_on_server
        elif style == "url":
            check_files_by_urls(tmpdir, base_url, [content_dict["path"]])
        assert content_dict["content"] == file_content


def run_ftp_stopped_test(ftpserver_fixture):
    """
    Tests if the Server is unreachable after shutdown, by checking if a client
    that tries to connect raises an exception.

    Parameters
    ----------
    ftpserver_fixture: PytestLocalFTPServer

    """
    ftpserver_fixture.stop()
    ftp = FTP()
    if USE_PROCESS:
        with pytest.raises((ConnectionRefusedError, ConnectionResetError)):
            ftp.connect("localhost", port=ftpserver_fixture.server_port)
    else:
        with pytest.raises(OSError):
            ftp.connect("localhost", port=ftpserver_fixture.server_port)


# ACTUAL TESTS


def test_ftpserver_class(ftpserver):
    assert isinstance(ftpserver, PytestLocalFTPServer)
    assert ftpserver.uses_TLS is False


@pytest.mark.parametrize("anon", [True, False])
def test_get_login_data(ftpserver, anon):
    login_dict = ftpserver.get_login_data(style="dict")
    assert login_dict["host"] == "localhost"
    assert login_dict["port"] == ftpserver.server_port
    if not anon:
        assert login_dict["user"] == "fakeusername"
        assert login_dict["passwd"] == "qweqwe"
    login_url = ftpserver.get_login_data(style="url", anon=anon)
    if anon:
        base_url = "ftp://localhost:"
    else:
        base_url = "ftp://fakeusername:qweqwe@localhost:"
    assert login_url == base_url + str(ftpserver.server_port)


def test_get_login_data_exceptions(ftpserver):
    # type errors
    with pytest.raises(
        TypeError,
        match="The Argument `style` needs to be of type "
        "``str``, the type given type was "
        "``bool``.",
    ):
        ftpserver.get_login_data(style=True)
    with pytest.raises(
        TypeError,
        match="The Argument `anon` needs to be of type "
        "``bool``, the type given type was "
        "``str``.",
    ):
        ftpserver.get_login_data(anon="not_bool")

    # value errors
    with pytest.raises(
        ValueError,
        match="The Argument `style` needs to be of value "
        "'dict' or 'url', the given value was "
        "'rel_path'.",
    ):
        ftpserver.get_login_data(style="rel_path")


@pytest.mark.parametrize("is_posix", [True, False])
@pytest.mark.parametrize("anon", [True, False])
def test_format_file_path(ftpserver, anon, is_posix):
    if is_posix:
        path_sep_char = "/"
    else:
        path_sep_char = "\\"
    base_url = ftpserver.get_login_data(style="url", anon=anon)

    rel_file_path = path_sep_char.join(["test_dir", "test_file"])
    rel_path = ftpserver.format_file_path(rel_file_path, anon=anon)
    assert rel_path == "test_dir/test_file"

    url_result = base_url + "/test_dir/test_file"
    url = ftpserver.format_file_path(rel_file_path, style="url", anon=anon)
    assert url == url_result


def test_format_file_path_exceptions(ftpserver):
    # type errors
    with pytest.raises(
        TypeError,
        match="The Argument `rel_file_path` needs to be of type "
        "``str``, the type given type was "
        "``int``.",
    ):
        ftpserver.format_file_path(1)
    # type errors
    with pytest.raises(
        TypeError,
        match="The Argument `style` needs to be of type "
        "``str``, the type given type was "
        "``bool``.",
    ):
        ftpserver.format_file_path("test/file", style=True)
    with pytest.raises(
        TypeError,
        match="The Argument `anon` needs to be of type "
        "``bool``, the type given type was "
        "``str``.",
    ):
        ftpserver.format_file_path("test/file", anon="not_bool")

    # value errors
    with pytest.raises(
        ValueError,
        match="The Argument `style` needs to be of value "
        "'rel_path' or 'url', the given value was "
        "'dict'.",
    ):
        ftpserver.format_file_path("test/file", style="dict")


@pytest.mark.parametrize("anon", [True, False])
def test_get_local_base_path(ftpserver, anon):
    # makes sure to start with clean temp dirs
    ftpserver.reset_tmp_dirs()
    local_path = ftpserver.get_local_base_path(anon=anon)
    assert os.path.isdir(local_path)
    if anon:
        path_substr = "anon_root_"
    else:
        path_substr = "ftp_home_"
    assert path_substr in local_path


def test_get_local_base_path_exceptions(ftpserver):
    # type errors
    with pytest.raises(
        TypeError,
        match="The Argument `anon` needs to be of type "
        "``bool``, the type given type was "
        "``str``.",
    ):
        ftpserver.get_local_base_path(anon="not_bool")


def test_file_upload_user(ftpserver, tmpdir):
    # makes sure to start with clean temp dirs
    ftpserver.reset_tmp_dirs()
    ftp = ftp_login(ftpserver)
    ftp.cwd("/")
    ftp.mkd("FOO")
    ftp.cwd("FOO")
    filename = "testfile.txt"
    file_path_local = tmpdir.join(filename)
    file_path_local.write("test")
    with open(str(file_path_local), "rb") as f:
        ftp.storbinary("STOR " + filename, f)
    close_client(ftp)

    assert os.path.isdir(os.path.join(ftpserver.server_home, "FOO"))
    abs_file_path_server = os.path.join(ftpserver.server_home, "FOO", filename)
    assert os.path.isfile(abs_file_path_server)
    with open(abs_file_path_server) as f:
        assert f.read() == "test"


def test_file_upload_anon(ftpserver):
    # anon user has no write privileges
    ftp = ftp_login(ftpserver, anon=True)
    ftp.cwd("/")
    with pytest.raises(error_perm):
        ftp.mkd("FOO")
    close_client(ftp)


@pytest.mark.parametrize("anon", [True, False])
def test_get_file_paths(tmpdir, ftpserver, anon):
    # makes sure to start with clean temp dirs
    ftpserver.reset_tmp_dirs()
    base_path = ftpserver.get_local_base_path(anon=anon)
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

    path_iterable = list(ftpserver.get_file_paths(anon=anon))
    assert len(path_iterable) == len(FILE_LIST)
    # checking the files by rel_path to user home dir
    # and native ftp client
    check_files_by_ftpclient(
            ftpserver,
            tmpdir,
            files_on_server,
            path_iterable,
            anon)

    # checking files by url
    url_iterable = list(ftpserver.get_file_paths(style="url", anon=anon))

    base_url = ftpserver.get_login_data(style="url", anon=anon)
    check_files_by_urls(tmpdir, base_url, url_iterable)


def test_get_file_paths_exceptions(ftpserver):
    # type errors
    with pytest.raises(
        TypeError,
        match="The Argument `style` needs to be of type "
        "``str``, the type given type was "
        "``bool``.",
    ):
        list(ftpserver.get_file_paths(style=True))

    with pytest.raises(
        TypeError,
        match="The Argument `anon` needs to be of type "
        "``bool``, the type given type was "
        "``str``.",
    ):
        list(ftpserver.get_file_paths(anon="not_bool"))

    # value errors
    with pytest.raises(
        ValueError,
        match="The Argument `style` needs to be of value "
        "'rel_path' or 'url', the given value was "
        "'dict'.",
    ):
        list(ftpserver.get_file_paths(style="dict"))


@pytest.mark.parametrize("anon", [True, False])
@pytest.mark.parametrize(
    "file_rel_paths",
    [None, "testfile1", ["testdir/testfile2", "testdir/nested/testfile3"]],
)
@pytest.mark.parametrize("style", ["rel_path", "url"])
@pytest.mark.parametrize("read_mode", ["r", "rb"])
def test_get_file_contents(
        tmpdir,
        ftpserver,
        anon,
        file_rel_paths,
        style,
        read_mode):
    ftpserver.reset_tmp_dirs()
    base_path = ftpserver.get_local_base_path(anon=anon)
    base_url = ftpserver.get_login_data(style="url", anon=anon)

    # write files to ftp home of user
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

    # tests for file_rel_paths being relative path
    if file_rel_paths is None:
        iterable_len = len(FILE_LIST)
    elif isinstance(file_rel_paths, str):
        iterable_len = 1
    else:
        iterable_len = len(file_rel_paths)

    path_list = list(
        ftpserver.get_file_contents(
            rel_file_paths=file_rel_paths,
            anon=anon,
            style=style,
            read_mode=read_mode
        )
    )

    check_get_file_contents(
        tmpdir=tmpdir,
        path_list=path_list,
        iterable_len=iterable_len,
        files_on_server=files_on_server,
        style=style,
        base_url=base_url,
        read_mode=read_mode,
    )

    with pytest.raises(
            ValueError,
            match=r"not a valid relative file path or url."):
        list(ftpserver.get_file_contents(
            rel_file_paths="not a file path",
            anon=anon))

    # tests for file_rel_paths being urls
    if isinstance(file_rel_paths, str):
        file_rel_paths = base_url + "/" + file_rel_paths
    elif isinstance(file_rel_paths, list):
        file_rel_paths = [
            base_url + "/" + file_rel_path for file_rel_path in file_rel_paths
        ]

    path_list = list(
        ftpserver.get_file_contents(
            rel_file_paths=file_rel_paths,
            anon=anon,
            style=style,
            read_mode=read_mode
        )
    )

    check_get_file_contents(
        tmpdir=tmpdir,
        path_list=path_list,
        iterable_len=iterable_len,
        files_on_server=files_on_server,
        style=style,
        base_url=base_url,
        read_mode=read_mode,
    )

    with pytest.raises(
            ValueError,
            match=r"not a valid relative file path or url."):
        list(
            ftpserver.get_file_contents(
                rel_file_paths="ftp://some-other-server", anon=anon
            )
        )


def test_get_file_contents_exceptions(ftpserver):
    # type errors
    with pytest.raises(
        TypeError,
        match="The Argument `rel_file_paths` needs to be of type "
        "``NoneType``, ``str`` or ``Iterable``, the type given "
        "type was ``int``.",
    ):
        list(ftpserver.get_file_contents(rel_file_paths=1))

    with pytest.raises(
        TypeError,
        match="The Argument `style` needs to be of type "
        "``str``, the type given type was "
        "``bool``.",
    ):
        list(ftpserver.get_file_contents(style=True))

    with pytest.raises(
        TypeError,
        match="The Argument `read_mode` needs to be of type "
        "``str``, the type given type was "
        "``bool``.",
    ):
        list(ftpserver.get_file_contents(read_mode=True))

    with pytest.raises(
        TypeError,
        match="The Argument `anon` needs to be of type "
        "``bool``, the type given type was "
        "``str``.",
    ):
        list(ftpserver.get_file_contents(anon="not_bool"))

    # value errors
    with pytest.raises(
        ValueError,
        match="The Argument `style` needs to be of value "
        "'rel_path' or 'url', the given value was "
        "'dict'.",
    ):
        list(ftpserver.get_file_contents(style="dict"))

    with pytest.raises(
        ValueError,
        match="The Argument `read_mode` needs to be of value "
        "'r' or 'rb', the given value was "
        "'invalid_option'.",
    ):
        list(ftpserver.get_file_contents(read_mode="invalid_option"))


@pytest.mark.parametrize("use_dict", [True, False])
@pytest.mark.parametrize("style", ["rel_path", "url"])
@pytest.mark.parametrize("anon", [True, False])
@pytest.mark.parametrize("overwrite", [True, False])
@pytest.mark.parametrize("return_paths", ["all", "input", "new"])
@pytest.mark.parametrize("return_content", [True, False])
@pytest.mark.parametrize("read_mode", ["r", "rb"])
def test_put_files(
    tmpdir,
    ftpserver,
    use_dict,
    style,
    anon,
    overwrite,
    return_paths,
    return_content,
    read_mode,
):
    """
    This test breaks if test_get_files breaks
    """
    # makes sure to start with clean temp dirs
    ftpserver.reset_tmp_dirs()
    base_url = ftpserver.get_login_data(style="url", anon=anon)
    files_on_server = []
    files_on_local = []
    local_dir = tmpdir.mkdir("local_dir")
    for dirs, filename in FILE_LIST:
        if dirs != "":
            test_file = local_dir.mkdir(dirs).join(filename)
        else:
            test_file = local_dir.join(filename)
        test_file.write(filename)
        if not use_dict:
            file_path = filename
            files_on_local.append(str(test_file))
        else:
            file_path = "/".join([dirs, filename]).lstrip("/")
            file_dict = {"src": str(test_file), "dest": file_path}
            files_on_local.append(file_dict)
        files_on_server.append(file_path)

    put_files_return = list(
        ftpserver.put_files(
            files_on_local=files_on_local,
            style=style,
            anon=anon,
            overwrite=overwrite,
            return_paths=return_paths,
            return_content=return_content,
            read_mode=read_mode,
        )
    )
    assert len(put_files_return) == len(FILE_LIST)

    if style == "rel_path":
        if not return_content:
            check_files_by_ftpclient(
                ftp_fixture=ftpserver,
                tmpdir=tmpdir,
                files_on_server=files_on_server,
                path_iterable=put_files_return,
                anon=anon,
            )
        else:
            check_get_file_contents(
                tmpdir=tmpdir,
                path_list=put_files_return,
                iterable_len=len(FILE_LIST),
                files_on_server=files_on_server,
                style=style,
                base_url=base_url,
                read_mode=read_mode,
            )

    elif style == "url":
        if not return_content:
            check_files_by_urls(
                tmpdir=tmpdir, base_url=base_url, url_iterable=put_files_return
            )
        else:
            check_get_file_contents(
                tmpdir=tmpdir,
                path_list=put_files_return,
                iterable_len=len(FILE_LIST),
                files_on_server=files_on_server,
                style=style,
                base_url=base_url,
                read_mode=read_mode,
            )

    # testing overwrite funtionality
    overwrite_file = files_on_local[0]

    if not use_dict:
        overwrite_result = os.path.split(overwrite_file)[1]
    else:
        overwrite_result = overwrite_file["dest"]
    overwrite_result = ftpserver.format_file_path(
        overwrite_result, style=style, anon=anon
    )

    if overwrite:
        overwrite_put_files_return = ftpserver.put_files(
            overwrite_file,
            style=style,
            anon=anon,
            overwrite=overwrite,
            return_paths=return_paths,
        )
        if return_paths == "new":
            assert overwrite_put_files_return == [overwrite_result]
        if return_paths == "input":
            assert overwrite_put_files_return == [overwrite_result]
        elif return_paths == "all":
            overwrite_result = list(
                ftpserver.get_file_paths(style=style, anon=anon))
            assert list(overwrite_put_files_return) == overwrite_result

    else:
        with pytest.warns(
                UserWarning,
                match=r"already exist and won't be overwritten"):
            overwrite_put_files_return = ftpserver.put_files(
                overwrite_file,
                style=style,
                anon=anon,
                overwrite=overwrite,
                return_paths=return_paths,
            )
            if return_paths == "new":
                assert overwrite_put_files_return == []
            elif return_paths == "input":
                assert overwrite_put_files_return == [overwrite_result]
            elif return_paths == "all":
                overwrite_result = list(
                    ftpserver.get_file_paths(style=style, anon=anon)
                )
                assert list(overwrite_put_files_return) == overwrite_result

    # delete local files
    local_dir.remove()


def test_put_files_exceptions(ftpserver, tmpdir):
    valid_file = tmpdir.join("valid_file")
    valid_file.write("valid_file")

    # testing with invalid "files"

    with pytest.raises(ValueError, match=r"is not a valid file path"):
        not_a_file = "not_a_file"
        ftpserver.put_files(not_a_file)

    with pytest.raises(ValueError, match=r"is not a valid file path"):
        not_a_file = {"src": "not_a_file", "dest": "does_not_matter"}
        ftpserver.put_files(not_a_file)

    # wrong/missing key for dict
    with pytest.raises(KeyError, match=r"the dicts need to have the Keys "):
        ftpserver.put_files({"wrong_key": "doesn't matter"})

    with pytest.raises(KeyError, match=r"the dicts need to have the Keys "):
        ftpserver.put_files({"src": "doesn't matter"})

    with pytest.raises(KeyError, match=r"the dicts need to have the Keys "):
        ftpserver.put_files({"dest": "doesn't matter"})

    # type errors in options

    with pytest.raises(TypeError, match=r"has to be of type"):
        ftpserver.put_files(
            1,
        )

    with pytest.raises(
        TypeError,
        match="The Argument `style` needs to be of type "
        "``str``, the type given type was "
        "``bool``.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4", style=True)

    with pytest.raises(
        TypeError,
        match="The Argument `anon` needs to be of type "
        "``bool``, the type given type was "
        "``str``.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4", anon="not_bool")

    with pytest.raises(
        TypeError,
        match="The Argument `overwrite` needs to be of type "
        "``bool``, the type given type was ``str``.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4", overwrite="not_bool"
        )

    with pytest.raises(
        TypeError,
        match="The Argument `return_paths` needs to be of type "
        "``str``, the type given type was ``bool``.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4", return_paths=True
        )

    with pytest.raises(
        TypeError,
        match="The Argument `return_content` needs to be of type "
        "``bool``, the type given type was ``str``.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4",
            return_content="not_bool"
        )

    with pytest.raises(
        TypeError,
        match="The Argument `read_mode` needs to be of type "
        "``str``, the type given type was ``bool``.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4",
            read_mode=True)

    # value errors
    with pytest.raises(
        ValueError,
        match="The Argument `style` needs to be of value "
        "'rel_path' or 'url', the given value was "
        "'dict'.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4",
            style="dict")

    with pytest.raises(
        ValueError,
        match="The Argument `return_paths` needs to be of value "
        "'all', 'input' or 'new', the given value was "
        "'invalid_option'.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4",
            return_paths="invalid_option"
        )

    with pytest.raises(
        ValueError,
        match="The Argument `read_mode` needs to be of value "
        "'r' or 'rb', the given value was "
        "'invalid_option'.",
    ):
        ftpserver.put_files(
            "doesn't matter since option check is be4",
            read_mode="invalid_option"
        )


def test_option_validator_logging(caplog, ftpserver):
    with caplog.at_level(logging.INFO):

        caplog.clear()

        ftpserver.__test_option_validator_logging__(1, 3)
        log_output = (
            "\n"
            "##################################################\n"
            "#       __TEST_OPTION_VALIDATOR_LOGGING__        #\n"
            "##################################################\n"
            "\n\n"
            "FUNC_LOCALS\n"
            "'a': 1\n"
            "'b': 3\n\n\n\n"
        )

        assert [log_output] == [rec.message for rec in caplog.records]


def test_ftp_stopped(ftpserver):
    local_anon_path = ftpserver.get_local_base_path(anon=True)
    local_ftp_home = ftpserver.get_local_base_path(anon=False)
    run_ftp_stopped_test(ftpserver)
    # check if all temp folders got cleared properly
    assert not os.path.exists(local_anon_path)
    assert not os.path.exists(local_ftp_home)


def test_fail_due_to_closed_module_scope(ftpserver):
    """This test is just meant to confirm that the server
    is down on module scope"""
    ftp = FTP()
    with pytest.raises(Exception):
        ftp.connect("localhost", port=ftpserver.server_port)

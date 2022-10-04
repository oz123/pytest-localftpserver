#!/usr/bin/env python

from collections.abc import Iterable
import logging
import os
import socket

import pytest

from pytest_localftpserver.helper_functions import (get_env_dict,
                                                    get_scope,
                                                    get_socket,
                                                    arg_validator,
                                                    pretty_logger,
                                                    DEFAULT_CERTFILE)


def test_get_env_dict():
    result_dict = {}
    result_dict["username"] = "fakeusername"
    result_dict["password"] = "qweqwe"
    result_dict["ftp_home"] = ""
    result_dict["ftp_port"] = 0
    result_dict["certfile"] = os.path.abspath(DEFAULT_CERTFILE)
    env_dict = get_env_dict()
    assert env_dict == result_dict


@pytest.mark.parametrize("env_var",
                         ["function", "module", "session"])
def test_get_scope(monkeypatch, env_var):
    monkeypatch.setenv('FTP_FIXTURE_SCOPE', env_var)
    assert get_scope() == env_var


def test_get_scope_warn(monkeypatch):
    monkeypatch.setenv('FTP_FIXTURE_SCOPE', "not_a_scope")
    with pytest.warns(
        UserWarning,
        match=r"The scope 'not_a_scope', given by the environment "
              r"variable 'FTP_FIXTURE_SCOPE' is not a valid scope, "
              r"which is why the default scope 'module'was used. "
              r"Valid scopes are 'function', 'module' and 'session'."):
        get_scope()


def test_get_socket():
    socket_obj, taken_port = get_socket()
    assert isinstance(socket_obj, socket.socket)
    assert isinstance(taken_port, int)
    with pytest.warns(
        UserWarning, match=r"PYTEST_LOCALFTPSERVER: "
                           r"The desire port {} was not free, so the "
                           r"server will run at port \d+.".format(taken_port)):
        socket_obj2, new_port = get_socket(taken_port)
        assert isinstance(socket_obj2, socket.socket)
        assert taken_port != new_port


def test_arg_validator():
    func_locals = {"test_str": "str",
                   "test_bool": True,
                   "test_int": 7,
                   "test_multi_type": "path_str"}
    valid_var_list = {
        "test_str":
            {"valid_values": ["str", "another_str"],
             "valid_types": [str]},
        "test_bool":
            {"valid_types": [bool]},
        "test_int":
            {"valid_values": [7],
             "valid_types": [int]},
        "test_multi_type":
            {"valid_types": [str, list, tuple]},
        "general_iterable":
            {"valid_types": [Iterable]}
    }
    # test valid_var_overwrite
    with pytest.raises(TypeError,
                       match="`valid_var_overwrite` needs to be a dict "
                             "of form:"):
        arg_validator({}, [], "fail")
    with pytest.raises(TypeError,
                       match="`valid_var_overwrite` needs to be a dict "
                             "of form:"):
        arg_validator({}, [], 1)
    with pytest.raises(TypeError,
                       match="`valid_var_overwrite` needs to be a dict "
                             "of form:"):
        arg_validator({}, [], {"arg_name": "not a dict"})
    missing_key_dict = {
        "random_key":
            {"valid_values and valid_types missing": 0}
    }
    with pytest.raises(KeyError,
                       match="`valid_var_overwrite` needs to be a dict "
                             "of form:"):
        arg_validator(func_locals, valid_var_list, missing_key_dict)
    arg_validator(func_locals, valid_var_list,
                  {"not_in_list": {"valid_types": [str]}})
    arg_validator(func_locals, valid_var_list,
                  {"test_str": {"valid_values": ["str"]}})
    # test type validation strict
    error_types = {"test_str": [1, "``str``", "int"],
                   "test_bool": ["True", "``bool``", "str"],
                   "test_int": [False, "``int``", "bool"],
                   "test_multi_type":
                   [False, "``str``, ``list`` or ``tuple``", "bool"]}
    for key, (val, type_str, given_type) in error_types.items():
        func_locals_wrong_type = dict(func_locals)
        func_locals_wrong_type[key] = val
        error_msg = "The Argument `{}` needs to be " \
                    "of type {}, the type given type was " \
                    "``{}``.".format(key, type_str, given_type)
        with pytest.raises(TypeError, match=error_msg):
            arg_validator(func_locals_wrong_type, valid_var_list)

    # test type validation not strict
    def test_generator_func():
        yield from [1, 2]

    test_generator = test_generator_func()

    error_types = [["test_int", False],
                   ["general_iterable", "str"],
                   ["general_iterable", [1, 2]],
                   ["general_iterable", {"key", "val"}],
                   ["general_iterable", test_generator]]
    func_locals_wrong_type = dict(func_locals)
    for key, val in error_types:
        func_locals_wrong_type[key] = val
        arg_validator(func_locals_wrong_type, valid_var_list,
                      valid_var_overwrite={"test_int": {"valid_values": [0]}},
                      strict_type_check=False)

    # test value validation
    error_values = {"test_str":
                    ["wrong value", "'str' or 'another_str'", "'wrong value'"],
                    "test_int": [1, "`7`", "`1`"]}
    for key, (val, value_string, given_value) in error_values.items():
        func_locals_wrong_value = dict(func_locals)
        func_locals_wrong_value[key] = val
        error_msg = "The Argument `{}` needs to be of value " \
                    "{}, the given value was " \
                    "{}.".format(key, value_string, given_value)
        with pytest.raises(ValueError, match=error_msg):
            arg_validator(func_locals_wrong_value, valid_var_list)
    # test missing missing entry warning
    func_locals_not_def_arg = dict(func_locals)
    func_locals_not_def_arg["new_arg"] = "this arg misses in valid_var_list"
    with pytest.warns(UserWarning, match=r"new_arg"):
        arg_validator(func_locals_not_def_arg, valid_var_list,
                      implementation_func_name="test_func", dev_mode=True)

    # little cheat for coverage.io ;)
    list(test_generator)


def test_pretty_logger(caplog):
    with caplog.at_level(logging.INFO):
        heading = "test_heading"
        msg = "{}".format("test_msg")
        caplog.clear()
        pretty_logger(heading, msg)
        log_output = "\n" \
                     "##################################################\n" \
                     "#                  test_heading                  #\n" \
                     "##################################################\n" \
                     "\n\n" \
                     "test_msg\n\n"

        assert [log_output] == [rec.message for rec in caplog.records]

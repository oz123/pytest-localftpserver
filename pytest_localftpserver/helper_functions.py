from copy import deepcopy
import logging
import os
import socket
import sys
from traceback import print_tb
import warnings

from ssl import SSLContext, SSLError
from ssl import PROTOCOL_TLS_CLIENT, TLSVersion

DEFAULT_CERTFILE = os.path.join(os.path.dirname(__file__),
                                "default_keycert.pem")


class InvalidCertificateError(Exception):
    pass


def get_env_dict(use_TLS=False):
    """
    Retrieves the environment variables used to configure
    the ftpserver fixtures

    Returns
    -------
    env_dict: dict
        Dict containing the environment variables used to configure
        the ftp fixtures or its default values.
    """
    env_dict = {}
    env_dict["username"] = os.getenv("FTP_USER", "fakeusername")
    env_dict["password"] = os.getenv("FTP_PASS", "qweqwe")
    if use_TLS:
        env_dict["ftp_home"] = os.getenv("FTP_HOME_TLS", "")
        env_dict["ftp_port"] = int(os.getenv("FTP_PORT_TLS", 0))
    else:
        env_dict["ftp_home"] = os.getenv("FTP_HOME", "")
        env_dict["ftp_port"] = int(os.getenv("FTP_PORT", 0))

    env_dict["certfile"] = os.path.abspath(os.getenv("FTP_CERTFILE",
                                                     DEFAULT_CERTFILE))
    return env_dict


def get_scope():
    """
    Retrieves the environment variables used to configure
    the ftpserver fixtures

    Returns
    -------
    scope: {'function', 'module', 'session'}: default 'module'
        Scope at which the fixture should be.

    """
    scope = os.getenv("FTP_FIXTURE_SCOPE", "module")
    if scope not in ["function", "module", "session"]:
        warnings.warn("The scope '{}', given by the environment variable 'FTP_FIXTURE_SCOPE' "
                      "is not a valid scope, which is why the default scope 'module'was used. "
                      "Valid scopes are 'function', 'module' and 'session'.".format(scope),
                      UserWarning)
        scope = "module"
    return scope


def validate_cert_file(cert_file):
    """

    Parameters
    ----------
    cert_file: str
        Path to the certfile to be checked.

    Raises
    ------

    InvalidCertificateError
        If the certificate is not valid.

    """
    cert_file = os.path.abspath(cert_file)
    try:
        context = SSLContext(PROTOCOL_TLS_CLIENT)
        context.minimum_version = TLSVersion.TLSv1_2
        context.maximum_version = TLSVersion.TLSv1_3
        context.load_cert_chain(cert_file)
    except SSLError as e:
        raise InvalidCertificateError("The certificate {}, you tried to use is not valid. "
                                      "Please make sure to use a working certificate or "
                                      "leave it unconfigured to use the default certificate. "
                                      "Details: {}"
                                      "".format(cert_file, e))


def get_socket(desired_port=0):
    """

    Parameters
    ----------
    desired_port: int
        Port which is desired to be used

    Returns
    -------
    (socket, port): tuple
        Serveraddress as tuple '(socket, port)'

    """
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        free_socket.bind(("", desired_port))
    except Exception:
        # Create a socket on any free port, if desired_port is taken
        free_socket.bind(("", 0))
    _, free_port = free_socket.getsockname()
    if desired_port != 0 and desired_port != free_port:
        warnings.warn("PYTEST_LOCALFTPSERVER: The desire port {} was not free, so the "
                      "server will run at port {}.".format(desired_port, free_port),
                      UserWarning)
    return free_socket, free_port


def pretty_logger(heading, msg):
    """
    Helper function to pretty log function output for debug purposes

    Parameters
    ----------
    heading: str
        Heading of the section which should be logged
    msg: str
        Message to be logged
    """
    heading_width = 50
    decoration_str = "\n" + "#"*heading_width + "\n"
    heading = "#" + heading.center(heading_width-2) + "#"
    heading = "{decoration_str}{heading}{decoration_str}\n\n".format(decoration_str=decoration_str,
                                                                     heading=heading)
    logging.info(heading+msg+"\n"*2)


def arg_validator_excepthook(exc_type, exc_value, exc_traceback):
    """
    This is a helper function for using `arg_validator`, which reduces the traceback
    to the calling function and the raised error_type and error_msg.
    This is done by overwriting `sys.excepthook` in case of an `Exception` caused by
    `arg_validator`(see Examples).
    The Parameter are the same as the output of `sys.exc_info()`

    Parameters
    ----------
    exc_type: type
        Exception type
    exc_value: str
        Exception message
    exc_traceback: traceback
        Traceback of the Exception

    Examples
    --------

    >>>import sys
    >>>from sys import excepthook as _excepthook
    >>>try:
    ...    sys.excepthook = _excepthook
    ...    arg_validator(func_locals, valid_var_list)
    ...except (ValueError, TypeError) as e:
    ...    sys.excepthook = arg_validator_excepthook
    ...    raise e
    """
    # since the excepthook will be caught by pytest there is no reason to
    # run it trought coverage
    print_tb(exc_traceback, limit=1, file=sys.stderr)  # pragma: no cover
    print(f"{exc_type.__name__}: {exc_value}", file=sys.stderr)  # pragma: no cover


def arg_validator(func_locals, valid_var_dict, valid_var_overwrite=None,
                  implementation_func_name="_option_validator",
                  strict_type_check=True, dev_mode=False):
    """
    Development helperfunction to raise appropriate Error if a methods/functions
    arg/kwarg is of wrong type or value.
    There are two ways of usage:
        One is to call the function directly after a
        function/Class/method is invoked:

        .. code:: python
            def func_to_test(argument_name, *args, **kwargs):
                func_locals = locals()
                valid_var_list = [{'name': 'argument_name',
                                   'valid_values':['test', {'test': 'testval'}],
                                   'valid_types':[str, dict]}]

                self.arg_validator(func_locals, valid_var_list)
                <function body>

        The other is to embed the function in a decorator:


        .. code:: python

            def arg_validator_decorator(f):

            valid_var_list = [{'name': 'argument_name',
                               'valid_values':['test', {'test': 'testval'}],
                               'valid_types':[str, dict]}]

                def wrapper(*args, **kwargs)
                    func_locals = dict(**dict(zip(f.__code__.co_varnames[1:], args)))
                    func_locals.update(kwargs)
                    arg_validator(func_locals, valid_var_list)

                    return f(*args, **kwargs)

                return wrapper

            @arg_validator_decorator
            def func_to_test(argument_name, *args, **kwargs):
                <function body>

    If a arg/kwarg isn't in the default values defined in `valid_var_list`
    add it to `valid_var_list` or use the option `valid_var_overwrite`,
    if it varies just in that case.


    Parameters
    ----------
    func_locals: dict
        The result of calling ``locals()`` at the very beginning of a method.
        If ``locals()`` is called later this might lead to problems with locally
        defined variables

    valid_var_dict: dict
        Dict of valid variables with the variable name as key and the value being
        a dict with keys 'valid_values'/'valid_types' which values are sequences:
        {'argument_name',
         'valid_values':['test', {'test': 'testval'}],
         'valid_types':[str, dict]
         }

    valid_var_overwrite: dict: default None
        This is used if in a special case, an args/kwargs value/type varies
        from the one defines in `valid_var_dict`

    Raises
    ------
    TypeError
        If any of the checked args/kwargs has a not supported type

    ValueError
        If any of the checked args/kwargs has a not supported value
    """
    # copy list by value (list1 = list2 would be copy by reference)
    valid_var_dict = deepcopy(valid_var_dict)
    # check if `valid_var_overwrite` has a valid form
    if valid_var_overwrite:
        error_msg = "`valid_var_overwrite` needs to be a dict of form:\n" \
                    "{'argument_name':\n" \
                    "   {'valid_values':['test', {'test': 'testval'}],\n" \
                    "    'valid_types':[str, dict]}\n" \
                    "}"
        if not isinstance(valid_var_overwrite, dict):
            raise TypeError(error_msg)

        for _, value_dict in valid_var_overwrite.items():
            if not isinstance(value_dict, dict):
                raise TypeError(error_msg)

            elif all([key not in value_dict.keys() for key in ["valid_values", "valid_types"]]):
                raise KeyError(error_msg)

    # update overwrites
        valid_var_dict.update(valid_var_overwrite)
    for key, val in func_locals.items():
        found_entry = False
        if key in valid_var_dict.keys():
            validate_dict = valid_var_dict[key]
            found_entry = True
            msg_dict = {"key": key, "val_type": type(val).__name__}
            if "valid_types" in validate_dict and len(validate_dict["valid_types"]):
                if strict_type_check:
                    # here ``type(val) in validate_dict["valid_types"]`` is used instead of
                    # isinstance(val, tuple(validate_dict["valid_types"])) because of false
                    # positives for isinstance(True, int), which may cause problems
                    invalid_type = type(val) not in validate_dict["valid_types"]
                else:
                    invalid_type = not isinstance(val, tuple(validate_dict["valid_types"]))
                if invalid_type:
                    valid_types = validate_dict["valid_types"]
                    if len(valid_types) == 1:
                        msg_dict["type_string"] = "``{}``" \
                                                  "".format(valid_types[0].__name__)
                    else:
                        valid_type_list = [f"``{valid_type.__name__}``"
                                           for valid_type in valid_types[:-1]]
                        base_str = ", ".join(valid_type_list)
                        msg_dict["type_string"] = "{} or ``{}``" \
                                                  "".format(base_str,
                                                            valid_types[-1].__name__)
                    raise TypeError("The Argument `{key}` needs to be of type "
                                    "{type_string}, the type given type was "
                                    "``{val_type}``.".format(**msg_dict))

            has_valid_values = "valid_values" in validate_dict and \
                               len(validate_dict["valid_values"])
            if has_valid_values and val not in validate_dict["valid_values"]:

                valid_values = validate_dict["valid_values"]

                if isinstance(val, str):
                    formater_str = "'{}'"
                else:
                    formater_str = "`{}`"
                if len(valid_values) == 1:
                    msg_dict["value_string"] = formater_str.format(valid_values[0])
                else:
                    valid_values_list = [formater_str.format(valid_value)
                                         for valid_value in valid_values[:-1]]
                    base_str = ", ".join(valid_values_list)
                    last_val_str = formater_str.format(valid_values[-1])
                    msg_dict["value_string"] = "{} or {}".format(base_str,
                                                                 last_val_str)
                msg_dict["val"] = formater_str.format(val)

                raise ValueError("The Argument `{key}` needs to be of value "
                                 "{value_string}, the given value was "
                                 "{val}.".format(**msg_dict))
        # this is a convenience functionality, for implementing new functions
        if not found_entry and dev_mode and key != "self":
            warn_msg = "`valid_var_list` in `{}` is missing an entry, " \
                       "where entry['name']=={}, this entry won't be " \
                       "validated.".format(implementation_func_name, key)
            warnings.warn(warn_msg, UserWarning)

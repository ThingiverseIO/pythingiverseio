from .libthingiverseio import tvio_error_message
from ctypes import c_int, c_void_p, byref, string_at


def _check_error(code):
    if code is not 0:
        msg = c_void_p()
        msg_size = c_int()
        tvio_error_message(code, byref(msg), byref(msg_size))
        raise Exception(string_at(msg, msg_size))

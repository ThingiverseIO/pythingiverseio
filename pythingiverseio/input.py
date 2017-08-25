from .error import _check_error
from .descriptor import check_descriptor
from .libthingiverseio import (tvio_new_input,
                               tvio_input_connected,
                               tvio_input_listen_result_available,
                               tvio_input_listen_start,
                               tvio_input_listen_stop,
                               tvio_input_listen_result_function,
                               tvio_input_listen_result_params,
                               tvio_input_listen_result_clear,
                               tvio_input_remove,
                               tvio_input_trigger,
                               tvio_input_trigger_all,
                               tvio_input_call)
from ctypes import c_int, c_char_p, c_void_p, byref, string_at
from .result import Result
import threading
from queue import Queue
import umsgpack
import time


class Input(threading.Thread):
    def __init__(self, descriptor):

        res = check_descriptor(descriptor)
        if len(res) != 0:
            raise Exception(res)

        self._input = tvio_new_input(c_char_p(descriptor.encode("ascii")))

        if self._input == -1:
            raise Exception("Error creating input")

        self._connected = False
        self._stop = threading.Event()

        self._listen_q = Queue()

        super(Input, self).__init__()

        self.setDaemon(True)
        self.setDaemon(True)
        self.start()

    def run(self):
        boolean = c_int()
        while not self._stop.is_set():
            _check_error(tvio_input_connected(self._input, byref(boolean)))
            self._connected = boolean.value == 1
            if self._connected:
                _check_error(tvio_input_listen_result_available(
                    self._input, byref(boolean)))
                if boolean.value is 1:
                    fun = c_char_p()
                    fun_size = c_int()
                    err = tvio_input_listen_result_function(self._input,
                                                            byref(fun),
                                                            byref(fun_size)
                                                            )
                    _check_error(err)

                    params = c_void_p()
                    params_size = c_int()
                    err = tvio_input_listen_result_params(self._input,
                                                          byref(params),
                                                          byref(params_size)
                                                          )
                    _check_error(err)

                    err = tvio_input_listen_result_clear(self._input)
                    _check_error(err)

                    self._listen_q.put(Result.from_listen(fun.value,
                                                          string_at(params,
                                                                    params_size
                                                                    )
                                                          )
                                       )

                else:
                    # TODO Maybe timeout (0)
                    self._stop.wait(0.01)
            else:
                self._stop.wait(0.01)

        _check_error(tvio_input_remove(self._input))

    def remove(self):
        self._stop.set()

    def connected(self):
        return self._connected

    def wait_until_connected(self, timeout=None):
        start = time.time()
        while not self.connected():
            if time.time() - start >= timeout:
                return True
            time.sleep(0.001)
        return False

    def call(self, function, parameter):
        packed = umsgpack.packb(parameter)
        uuid = c_char_p()
        uuid_size = c_int()
        err = tvio_input_call(self._input, c_char_p(function.encode("ascii")),
                              packed,
                              len(packed),
                              byref(uuid),
                              byref(uuid_size)
                              )
        _check_error(err)
        return Result(self, uuid=uuid)

    def trigger(self, function, parameter):
        packed = umsgpack.packb(parameter)
        err = tvio_input_trigger(self._input,
                                 c_char_p(function.encode("ascii")),
                                 packed,
                                 len(packed))
        _check_error(err)

    def trigger_all(self, function, parameter):
        packed = umsgpack.packb(parameter)
        err = tvio_input_trigger_all(self._input,
                                     c_char_p(function.encode("ascii")),
                                     packed,
                                     len(packed))
        _check_error(err)

    def start_listen(self, function):
        _check_error(tvio_input_listen_start(self._input,
                                             c_char_p(function.encode("ascii"))
                                             ))

    def stop_listen(self, function):
        _check_error(tvio_input_listen_stop(self._input,
                                            c_char_p(function.encode("ascii"))
                                            ))

    def listen(self, timeout=None):
        return self._listen_q.get(timeout=timeout)

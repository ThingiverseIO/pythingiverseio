from .libthingiverseio import tvio_result_ready, tvio_retrieve_result_params
from ctypes import c_int, c_void_p, byref, string_at
import umsgpack
import threading
import time


class Result(threading.Thread):
    def __init__(self, input=None, uuid=None):
        if uuid is not None and input is not None:
            self._received = False
            self._input = input
            super(Result, self).__init__()
            self._uuid = uuid
            self.setDaemon(True)
            self.start()

    @classmethod
    def from_listen(cls, function, params):
            res = cls()
            res._received = True
            res._function = function
            res._params = params
            return res

    def run(self):
        ready = c_int()

        while not self._received and not self._input._stop.is_set():
            _check_error(tvio_result_ready(self._input._input,
                         self._uuid, byref(ready)))
            self._received = ready.value is 1
            time.sleep(0.01)

        params = c_void_p()
        params_size = c_int()
        err = tvio_retrieve_result_params(self._input._input,
                                          self._uuid,
                                          byref(params),
                                          byref(params_size)
                                          )
        _check_error(err)

        self._params = string_at(params, params_size)

    def received(self):
        return self._received

    def parameter(self):
        if not self._received:
            return None
        return umsgpack.unpackb(self._params)


def _check_error(err):
    if err != 0:
        raise Exception("Tvio Error")

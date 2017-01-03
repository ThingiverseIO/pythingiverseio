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

        while True:
            _check_error(tvio_result_ready(self._input._input,
                         self._uuid, byref(ready)))
            if ready.value is 1:
                break
            if self._input._stop.is_set():
                return
            time.sleep(0.001)

        params = c_void_p()
        params_size = c_int()
        err = tvio_retrieve_result_params(self._input._input,
                                          self._uuid,
                                          byref(params),
                                          byref(params_size)
                                          )
        _check_error(err)

        self._params = string_at(params, params_size)
        self._received = True

    def received(self):
        return self._received

    def wait_until_received(self, timeout=1):
        start = time.time()
        while not self.received():
            if time.time() - start >= timeout:
                return True
            time.sleep(0.001)
        return False

    def parameter(self):
        if not self._received:
            return None
        return umsgpack.unpackb(self._params)


def _check_error(err):
    if err != 0:
        raise Exception("Tvio Error")

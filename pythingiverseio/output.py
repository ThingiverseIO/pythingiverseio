# Copyright (c) 2016 Joern Weissenborn
#
# This file is part of pythingiverseio.
#
# aursir4py is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# aursir4py is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pythingiverseio.  If not, see <http://www.gnu.org/licenses/>.

from .error import _check_error
from .libthingiverseio import (
                               tvio_new_output,
                               tvio_output_remove,
                               tvio_output_request_available,
                               tvio_output_request_function,
                               tvio_output_request_id,
                               tvio_output_request_params,
                               )
from ctypes import byref, c_int, c_char_p, c_void_p, string_at
from .descriptor import check_descriptor
from .request import Request
import threading
from queue import Queue

_author__ = 'Joern Weissenborn'


class Output(threading.Thread):
    def __init__(self, descriptor):

        res = check_descriptor(descriptor)
        if len(res) != 0:
            raise Exception(res)

        self._output = tvio_new_output(c_char_p(descriptor.encode("ascii")))

        if self._output == -1:
            raise Exception("Error creating output")

        self._connected = False
        self._stop = threading.Event()

        self._request_q = Queue()

        super(Output, self).__init__()

        self.setDaemon(True)
        self.start()

    def run(self):
        req_available = c_int()
        while not self._stop.is_set():
            _check_error(tvio_output_request_available(self._output,
                                                       byref(req_available)))
            if req_available.value is 1:
                uuid = c_char_p()
                uuid_size = c_int()
                err = tvio_output_request_id(self._output,
                                             byref(uuid),
                                             byref(uuid_size)
                                             )
                _check_error(err)

                fun = c_char_p()
                fun_size = c_int()
                err = tvio_output_request_function(self._output,
                                                   uuid,
                                                   byref(fun),
                                                   byref(fun_size)
                                                   )
                _check_error(err)

                params = c_void_p()
                params_size = c_int()
                err = tvio_output_request_params(c_int(self._output),
                                                 uuid,
                                                 byref(params),
                                                 byref(params_size))
                _check_error(err)

                self._request_q.put(Request(self._output, uuid,
                                            fun.value.decode("ascii"),
                                            string_at(params, params_size)))
            else:
                self._stop.wait(0.01)
        _check_error(tvio_output_remove(self._output))

    def remove(self):
        self._stop.set()

    def get_request(self, timeout=None):
        return self._request_q.get(timeout=timeout)

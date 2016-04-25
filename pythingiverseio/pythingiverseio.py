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

_author__ = 'Joern Weissenborn'

import libthingiverseio
import time
import threading
import Queue
import msgpack
import io

def flavour_descriptor(desc, flavour):
    return desc + '\n' + flavour

def profile_descriptor(desc, profile):
    if type(profile) is list:
        tags = "tags"
        for t in profile:
            tags = tags + " " + t
        return flavour_descriptor(desc, tags)
    return flavour_descriptor(desc, "tag " + profile)

def profile_descriptor_key_value(desc, key, value):
    return profile_descriptor(desc, key + ":" + value)

def version():
    pmaj = libthingiverseio.new_intp()
    pmin = libthingiverseio.new_intp()
    pfix = libthingiverseio.new_intp()

    _check_error(libthingiverseio.tvio_version(pmaj, pmin, pfix))

    maj = libthingiverseio.intp_value(pmaj)
    libthingiverseio.delete_intp(pmaj)

    min = libthingiverseio.intp_value(pmin)
    libthingiverseio.delete_intp(pmin)

    fix = libthingiverseio.intp_value(pfix)
    libthingiverseio.delete_intp(pfix)

    return maj, min, fix

def check_descriptor(desc):
    if type(desc) is not str:
        raise ValueError('Descriptor must be a string!')
    return libthingiverseio.tvio_check_descriptor(desc)

class Input(threading.Thread):
    def __init__(self, descriptor):

        res = check_descriptor(descriptor)
        if len(res) != 0:
            raise Exception(res)

        self._input = libthingiverseio.tvio_new_input(descriptor)

        if self._input == -1:
            raise Exception("Error creating input")

        self._connected = False
        self._stop = threading.Event()

        self._listen_q = Queue.Queue()

        super(Input, self).__init__()

        self.setDaemon(True)
        self.setDaemon(True)
        self.start()

    def run(self):
        pis = libthingiverseio.new_intp()
        while not self._stop.is_set():
            _check_error(libthingiverseio.tvio_connected(self._input,pis))
            self._connected = (libthingiverseio.intp_value(pis) == 1)
            if self._connected:
                _check_error(libthingiverseio.tvio_listen_result_available(self._input,
                                                                           pis))
                if libthingiverseio.intp_value(pis) == 1:
                    err, fun = libthingiverseio.tvio_retrieve_listen_result_function(self._input)
                    _check_error(err)
                    err, params = libthingiverseio.tvio_retrieve_listen_result_params(self._input)
                    _check_error(err)

                    self._listen_q.put(Result.from_listen(fun, params))

                else:
                    self._stop.wait(0.01)
            else:
                self._stop.wait(0.01)


        libthingiverseio.delete_intp(pis)
        _check_error(libthingiverseio.tvio_remove_input(self._input))

    def remove(self):
        self._stop.set()

    def connected(self):
        return self._connected

    def call(self, function, parameter):
        packed = msgpack.packb(parameter)
        err, id = libthingiverseio.tvio_call(self._input, function, packed,
                                             len(packed))
        _check_error(err)
        return Result(self, id=id)

    def trigger(self, function, parameter):
        packed = msgpack.packb(parameter)
        err = libthingiverseio.tvio_trigger(self._input, function, packed,
                                             len(packed))
        _check_error(err)

    def trigger_all(self, function, parameter):
        packed = msgpack.packb(parameter)
        err = libthingiverseio.tvio_trigger(self._input, function, packed,
                                             len(packed))
        _check_error(err)

    def start_listen(self, function):
        _check_error(libthingiverseio.tvio_start_listen(self._input, function))

    def stop_listen(self, function):
        _check_error(libthingiverseio.tvio_stop_listen(self._input, function))

    def listen(self, timeout=None):
        return self._listen_q.get(timeout=timeout)

class Output(threading.Thread):
    def __init__(self, descriptor):

        res = check_descriptor(descriptor)
        if len(res) != 0:
            raise Exception(res)

        self._output = libthingiverseio.tvio_new_output(descriptor)

        if self._output == -1:
            raise Exception("Error creating output")

        self._connected = False
        self._stop = threading.Event()

        self._request_q = Queue.Queue()

        super(Output, self).__init__()

        self.setDaemon(True)
        self.start()

    def run(self):
        preq_available = libthingiverseio.new_intp()
        while not self._stop.is_set():
            _check_error(libthingiverseio.tvio_request_available(self._output,
                                                                 preq_available))
            if libthingiverseio.intp_value(preq_available) is 1:
                err, id = libthingiverseio.tvio_get_next_request_id(self._output)
                _check_error(err)
                err, fun = libthingiverseio.tvio_retrieve_request_function(self._output,
                                                                id)
                _check_error(err)
                err, params = libthingiverseio.tvio_retrieve_request_params(self._output,
                                                              id)
                _check_error(err)
                self._request_q.put(Request(self._output, id, fun, params))
            else:
                self._stop.wait(0.01)
        libthingiverseio.delete_intp(preq_available)
        _check_error(libthingiverseio.tvio_remove_output(self._output))

    def remove(self):
        self._stop.set()

    def get_request(self, timeout=None):
        return self._request_q.get(timeout=timeout)

class Result(threading.Thread):
    def __init__(self, input=None, id=None):
        if id is not None and input is not None:
            self._received = False
            self._input = input
            super(Result, self).__init__()
            self._id = id
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
        pready = libthingiverseio.new_intp()

        while not self._received and not self._input._stop.is_set():
            _check_error(libthingiverseio.tvio_result_ready(self._input._input,
                                                            self._id, pready))
            self._received = libthingiverseio.intp_value(pready)
            time.sleep(0.01)

        libthingiverseio.delete_intp(pready)
        if not self._input._stop.is_set():
            err, self._params = libthingiverseio.tvio_retrieve_result_params(self._input._input, self._id)
            _check_error(err)

    def received(self):
        return self._received

    def parameter(self):
        if not self._received:
            return None
        return msgpack.unpackb(self._params)


class Request():
    def __init__(self, output, id, function, params):
        self._output = output
        self._id = id
        self._function = function
        self._params = params

    def function(self):
        return self._function

    def parameter(self):
        return msgpack.unpackb(self._params)

    def reply(self, params):
        packed = msgpack.packb(params)
        _check_error(libthingiverseio.tvio_reply(self._output, self._id,
                                                 packed, len(packed)))

def _check_error(err):
    if err != 0:
        raise Exception("Tvio Error")

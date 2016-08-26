from .libthingiverseio import tvio_reply
import umsgpack


class Request():
    def __init__(self, output, id, function, params):
        self._output = output
        self._id = id
        self._function = function
        self._params = params

    def function(self):
        return self._function

    def parameter(self):
        return umsgpack.unpackb(self._params)

    def reply(self, params):
        packed = umsgpack.packb(params)
        _check_error(tvio_reply(self._output, self._id,
                     packed, len(packed)))


def _check_error(err):
    if err != 0:
        raise Exception("Tvio Error")

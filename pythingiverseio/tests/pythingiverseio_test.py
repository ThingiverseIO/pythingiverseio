import pythingiverseio
import time
from unittest import TestCase

DESCRIPTOR = "func SayHello(Greeting string) (Answer string)"


class TestPythingiverseio(TestCase):
    def test_basics(self):
        input = pythingiverseio.Input(DESCRIPTOR)
        self.assertTrue(input is not -1)

        self.assertTrue(not input.connected())

        output = pythingiverseio.Output(DESCRIPTOR)

        self.assertTrue(output is not -1)

        time.sleep(2)

        self.assertTrue(input.connected())

        input.remove()
        output.remove()

    def test_call(self):
        input = pythingiverseio.Input(DESCRIPTOR)
        output = pythingiverseio.Output(DESCRIPTOR)
        res = input.call("SayHello",{"Greeting":"test_py"})

        req = output.get_request()
        params = req.parameter()
        self.assertTrue(req.function() == "SayHello")
        self.assertTrue(params[b"Greeting"] == b"test_py")

        req.reply({"Answer": "test_ok"})

        time.sleep(1)

        self.assertTrue(res.received())

        params = res.parameter()
        self.assertTrue(params[b"Answer"] == b"test_ok")

        input.remove()
        output.remove()

    def test_trigger(self):
        input = pythingiverseio.Input(DESCRIPTOR)
        input.start_listen("SayHello")


        output = pythingiverseio.Output(DESCRIPTOR)

        time.sleep(2)
        input.trigger("SayHello",{"Greeting":"test_py"})

        req = output.get_request(timeout=1)
        params = req.parameter()
        self.assertTrue(req.function() == "SayHello")
        self.assertTrue(params[b"Greeting"] == b"test_py")

        req.reply({"Answer":"test_ok"})


        res = input.listen(timeout=5)

        params = res.parameter()
        self.assertTrue(params[b"Answer"] == b"test_ok")

        input.remove()
        output.remove()

import pythingiverseio

DESCRIPTOR = "func SayHello(Greeting string) (Answer string)"


def main():

    input = pythingiverseio.Input(DESCRIPTOR)

    result = input.call("SayHello", {"Greeting": "Hello from pythingiverseio!"})

    result.wait_until_received(timeout=10)

    print(result.parameter())


if __name__ == "__main__":
    main()

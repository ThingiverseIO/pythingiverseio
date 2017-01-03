
import pythingiverseio

DESCRIPTOR = "func SayHello(Greeting string) (Answer string)"


def main():

    input = pythingiverseio.Input(DESCRIPTOR)

    input.start_listen("SayHello")

    input.wait_until_connected(timeout=10)

    input.trigger("SayHello", {"Greeting": "Hello from pythingiverseio!"})

    print(input.listen().parameter())


if __name__ == "__main__":
    main()

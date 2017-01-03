import pythingiverseio

DESCRIPTOR = "func SayHello(Greeting string) (Answer string)"


def main():
    output = pythingiverseio.Output(DESCRIPTOR)

    while True:
        request = output.get_request()

        print(request.parameter())

        request.reply({"Answer":"Greetings back from pythingiverseio!"})


if __name__ == "__main__":
    main()

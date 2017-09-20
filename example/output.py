import pythingiverseio

DESCRIPTOR = """
function SayHello(Greeting string) (Answer string)
property Mood: Feeling string
tag example_tag
"""


def main():
    output = pythingiverseio.Output(DESCRIPTOR)
    output.set_property("Mood", {"Feeling":"Extraordinary"})

    while True:
        request = output.get_request()

        print(request.parameter())

        request.reply({"Answer":"Greetings back from pythingiverseio!"})


if __name__ == "__main__":
    main()

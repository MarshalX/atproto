from atproto import Client


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    client.send_post(text='Hello World from Python!')


if __name__ == '__main__':
    main()

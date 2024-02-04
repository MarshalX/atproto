from atproto import Client


def main() -> None:
    # This is an example for get_follows method.
    client = Client()
    client.login('my-handle', 'my-password')
    handle = 'target-handle'

    cursor = None
    follows = []

    while True:
        fetched = client.get_follows(actor=handle, cursor=cursor)
        follows = follows + fetched.follows

        if not fetched.cursor:
            break

        cursor = fetched.cursor

    print(follows)


if __name__ == '__main__':
    main()

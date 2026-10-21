from atproto import Client, models


def main() -> None:
    # This is an example for get_follows method. client_utils.paginate does the same: see paginate_follows.py
    client = Client()
    client.login('my-handle', 'my-password')
    handle = 'target-handle'

    cursor = None
    follows: list[models.AppBskyActorDefs.ProfileView] = []

    while True:
        fetched = client.get_follows(actor=handle, cursor=cursor)
        follows = follows + fetched.follows

        if not fetched.cursor:
            break

        cursor = fetched.cursor

    print(follows)


if __name__ == '__main__':
    main()

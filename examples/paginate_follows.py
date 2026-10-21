from atproto import Client, client_utils


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # Fetches page after page until the end. The same loop by hand: advanced_usage/handle_cursor_pagination.py
    follows = client_utils.paginate(client.app.bsky.graph.get_follows, {'actor': 'target-handle', 'limit': 100})
    for profile in follows.items():
        print(profile.handle)


if __name__ == '__main__':
    main()

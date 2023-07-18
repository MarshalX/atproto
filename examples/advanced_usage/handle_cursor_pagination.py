import typing as t

from atproto import Client
from atproto.xrpc_client import models


def main():
    # This is an example for get_follows method.
    client = Client()
    client.login('my-handle', 'my-password')
    handle = 'target-handle'

    def _fetch(actor: str, cursor: t.Union[str, None]) -> models.AppBskyGraphGetFollows.Response:
        params = models.AppBskyGraphGetFollows.Params(actor=actor, limit=100)
        if cursor:
            params.cursor = cursor

        return client.bsky.graph.get_follows(params)

    cursor = None
    follows = []

    while True:
        fetched = _fetch(handle, cursor)
        if not fetched.cursor:
            break

        follows = follows + fetched.follows
        cursor = fetched.cursor

    print(follows)


if __name__ == '__main__':
    main()

"""Keep bookmarks in a personal space, which only the account and the applications it authorized can read.

The space is created on the first run. Its key is ``self``, so an account has one bookmarks space.
The NSIDs are placeholders: use a space type and a collection under a domain of your own.
The PDS resolves the lexicon of the space type when the account authorizes the application,
so the login fails with ``invalid_scope`` until the type is published as a lexicon of type ``space``.

Spaces are in alpha, so the PDS of the account has to support them.

    python bookmarks.py alice.example.com                      # list the bookmarks
    python bookmarks.py alice.example.com https://atproto.com  # add one first
"""

import sys
import typing as t

from atproto import Client, JsonFileStore, OAuthClient, OAuthSession, SpaceClient, SpaceType, models
from atproto.exceptions import OAuthError

BOOKMARK = 'com.example.bookmark'
BOOKMARKS = SpaceType('com.example.bookmarks', key='literal:self', collections=(BOOKMARK,))

# the bookmarks space of the account itself: read it, write bookmarks to it, and create it
SCOPE = f'atproto space:{BOOKMARKS.nsid}?collection={BOOKMARK}&manage=create'
SESSION_FILE = 'bookmarks-session.json'


def get_session(oauth_client: OAuthClient, identifier: str) -> OAuthSession:
    try:
        return oauth_client.restore(identifier)
    except OAuthError:
        return oauth_client.login_with_browser(identifier)


def open_bookmarks(client: Client, did: str) -> SpaceClient:
    spaces = client.com.atproto.space.list_spaces({'space_type': BOOKMARKS.nsid, 'space_did': did}).spaces
    if spaces:
        return SpaceClient(client, spaces[0].space, BOOKMARKS)

    return SpaceClient.create_space(client, BOOKMARKS, models.ComAtprotoPersonalspacePolicy.Main())


def main(identifier: str, url: t.Optional[str]) -> None:
    oauth_client = OAuthClient.loopback(scope=SCOPE, session_store=JsonFileStore(SESSION_FILE))
    session = get_session(oauth_client, identifier)

    client = Client()
    client.login_oauth(session)

    bookmarks = open_bookmarks(client, session.did)
    print(f'Bookmarks of {session.did} are in {bookmarks.uri}')

    if url:
        bookmarks.create_record({'$type': BOOKMARK, 'subject': url, 'createdAt': client.get_current_time_iso()})

    for record in bookmarks.records(collection=BOOKMARK):
        print(record.rkey, record.value.subject)


if __name__ == '__main__':
    if len(sys.argv) not in (2, 3):
        sys.exit(f'Usage: {sys.argv[0]} <handle or DID> [URL to bookmark]')

    main(sys.argv[1], sys.argv[2] if len(sys.argv) == 3 else None)

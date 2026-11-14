"""Log in from the command line with OAuth and make an authenticated request.

A loopback client needs no hosted client metadata: the authorization server accepts
``http://localhost`` as the client ID and redirects the browser back to a port on this machine.

The session is kept in ``oauth-session.json``. Run the script again to reuse it without the browser.

    python loopback_cli.py alice.bsky.social
"""

import sys
import webbrowser

from atproto import Client, JsonFileStore, OAuthClient, OAuthSession, models
from atproto.exceptions import OAuthError

# ask only for what the script does: create posts
SCOPE = f'atproto repo:{models.ids.AppBskyFeedPost}?action=create'
SESSION_FILE = 'oauth-session.json'


def open_browser(url: str) -> None:
    print('Opening the browser. If nothing happens, open this URL yourself:')
    print(url)
    webbrowser.open(url)


def get_session(oauth_client: OAuthClient, identifier: str) -> OAuthSession:
    try:
        return oauth_client.restore(identifier)
    except OAuthError:
        return oauth_client.login_with_browser(identifier, open_url=open_browser)


def main(identifier: str) -> None:
    oauth_client = OAuthClient.loopback(scope=SCOPE, session_store=JsonFileStore(SESSION_FILE))

    session = get_session(oauth_client, identifier)
    print(f'Logged in as {session.did} with scope: {session.get_token_info().scope}')

    client = Client()
    client.login_oauth(session)

    post = client.send_post('Hello from the OAuth example of the atproto Python SDK!')
    print(f'Posted: {post.uri}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'Usage: {sys.argv[0]} <handle or DID>')

    main(sys.argv[1])

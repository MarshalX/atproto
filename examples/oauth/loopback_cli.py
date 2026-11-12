"""Log in from the command line with OAuth and make an authenticated request.

A loopback client needs no hosted client metadata: the authorization server accepts
``http://localhost`` as the client ID and redirects the browser back to a port on this machine.

The session is kept in ``oauth-session.json``. Run the script again to reuse it without the browser.

    python loopback_cli.py alice.bsky.social
"""

import sys
import threading
import typing as t
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qsl, urlsplit

import typing_extensions as te
from atproto import Client
from atproto_oauth import JsonFileStore, OAuthClient, OAuthSession
from atproto_oauth.exceptions import OAuthError

# ask only for what the script does: create posts
SCOPE = 'atproto repo:app.bsky.feed.post?action=create'
SESSION_FILE = 'oauth-session.json'
CALLBACK_PATH = '/callback'


class _CallbackHandler(BaseHTTPRequestHandler):
    params: t.ClassVar[t.Dict[str, str]] = {}
    received: t.ClassVar[threading.Event] = threading.Event()

    def do_GET(self) -> None:
        url = urlsplit(self.path)
        if url.path != CALLBACK_PATH:
            self.send_error(404)
            return

        type(self).params = dict(parse_qsl(url.query))
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(b'You can close this tab and return to the terminal.')
        self.received.set()

    @te.override
    def log_message(self, format: str, *args: t.Any) -> None:
        pass


def make_oauth_client(port: t.Optional[int] = None) -> OAuthClient:
    # the client ID does not include the port, so the client that restores a session is the one that created it
    host = '127.0.0.1' if port is None else f'127.0.0.1:{port}'

    return OAuthClient.loopback(
        redirect_uri=f'http://{host}{CALLBACK_PATH}',
        scope=SCOPE,
        session_store=JsonFileStore(SESSION_FILE),
    )


def login(identifier: str) -> OAuthSession:
    # port 0 lets the system pick a free port; the authorization server ignores the port of a loopback redirect
    server = HTTPServer(('127.0.0.1', 0), _CallbackHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    oauth_client = make_oauth_client(server.server_port)

    try:
        url = oauth_client.authorize(identifier)
        print('Opening the browser. If nothing happens, open this URL yourself:')
        print(url)
        webbrowser.open(url)

        _CallbackHandler.received.wait()

        return oauth_client.callback(_CallbackHandler.params).session
    finally:
        server.shutdown()


def restore(identifier: str) -> t.Optional[OAuthSession]:
    oauth_client = make_oauth_client()
    did = identifier if identifier.startswith('did:') else oauth_client.resolver.resolve_identity(identifier).did

    try:
        return oauth_client.restore(did)
    except OAuthError:
        return None


def main(identifier: str) -> None:
    session = restore(identifier) or login(identifier)
    print(f'Logged in as {session.did} with scope: {session.get_token_info().scope}')

    client = Client()
    client.login_oauth(session)

    post = client.send_post('Hello from the OAuth example of the atproto Python SDK!')
    print(f'Posted: {post.uri}')


if __name__ == '__main__':
    if len(sys.argv) != 2:
        sys.exit(f'Usage: {sys.argv[0]} <handle or DID>')

    main(sys.argv[1])

import socket
import threading
import typing as t
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlsplit

import typing_extensions as te

from atproto_oauth._effects import Flow, call, call_blocking
from atproto_oauth.exceptions import OAuthCallbackError
from atproto_oauth.metadata import is_loopback_redirect_uri

DEFAULT_LOGIN_TIMEOUT: t.Final = 300.0
_CALLBACK_PAGE: t.Final = b'You can close this tab and return to the application.'
# closing the server blocks the caller for up to this long
_POLL_INTERVAL: t.Final = 0.05


class _Server(ThreadingHTTPServer):
    def __init__(self, address: t.Tuple[str, int], callback_path: str) -> None:
        if ':' in address[0]:
            self.address_family = socket.AF_INET6

        super().__init__(address, _Handler)
        self.callback_path = callback_path
        self.params: t.Optional[t.Dict[str, str]] = None
        self.received = threading.Event()


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        server = t.cast('_Server', self.server)

        url = urlsplit(self.path)
        if url.path != server.callback_path or server.received.is_set():
            self.send_error(404)
            return

        server.params = dict(parse_qsl(url.query))
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.send_header('Content-Length', str(len(_CALLBACK_PAGE)))
        self.end_headers()
        self.wfile.write(_CALLBACK_PAGE)
        server.received.set()

    @te.override
    def log_message(self, format: str, *args: t.Any) -> None:
        pass


class LoopbackCallbackServer:
    """Local HTTP server that receives the redirect back from the authorization server.

    Args:
        redirect_uris: Redirect URIs of the client. The first loopback one is served;
            without a port in it, the system picks a free one.

    Raises:
        :class:`ValueError`: None of the redirect URIs is a loopback one.
    """

    def __init__(self, redirect_uris: t.Sequence[str]) -> None:
        registered = next((uri for uri in redirect_uris if is_loopback_redirect_uri(uri)), None)
        if registered is None:
            raise ValueError('The client has no redirect URI on 127.0.0.1 or [::1]')

        parts = urlsplit(registered)
        hostname = parts.hostname or ''
        self._server = _Server((hostname, parts.port or 0), parts.path or '/')

        host = f'[{hostname}]' if ':' in hostname else hostname
        self.redirect_uri = parts._replace(netloc=f'{host}:{self._server.server_port}').geturl()

        self._thread = threading.Thread(target=self._server.serve_forever, args=(_POLL_INTERVAL,), daemon=True)
        self._thread.start()

    def __enter__(self) -> te.Self:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()

    def wait(self, timeout: t.Optional[float] = None) -> t.Dict[str, str]:
        """Block until the redirect arrives and return its query parameters.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthCallbackError`: Nothing arrived in time.
        """
        self._server.received.wait(timeout)
        if self._server.params is None:
            raise OAuthCallbackError('The authorization was not completed in time')

        return self._server.params

    def close(self) -> None:
        # a cancelled login leaves a thread waiting for the redirect
        self._server.received.set()
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()


def login_flow(
    client: t.Any,
    identifier: str,
    open_url: t.Callable[[str], t.Any],
    timeout: t.Optional[float],
    params: t.Mapping[str, t.Any],
) -> Flow[t.Any]:
    with LoopbackCallbackServer(client.client_metadata['redirect_uris']) as server:
        url = yield call(client.authorize, identifier, redirect_uri=server.redirect_uri, **params)
        open_url(url)

        callback_params = yield call_blocking(server.wait, timeout)
        result = yield call(client.callback, callback_params)

    return result.session

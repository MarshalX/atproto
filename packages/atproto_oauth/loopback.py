import socket
import socketserver
import threading
import typing as t
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qsl, urlsplit

import typing_extensions as te

from atproto_oauth._effects import Flow, call, call_blocking
from atproto_oauth.exceptions import OAuthCallbackError
from atproto_oauth.metadata import is_loopback_redirect_uri

DEFAULT_LOGIN_TIMEOUT: t.Final = 300.0
_PAGE: t.Final = (
    '<!DOCTYPE html><html><head><meta charset="utf-8"><title>{0}</title></head><body><p>{0}</p></body></html>'
)
_SUCCESS_MESSAGE: t.Final = 'Authorization complete. You can close this tab and return to the application.'
_FAILURE_MESSAGE: t.Final = 'Authorization failed. You can close this tab and return to the application.'
# closing the server blocks the caller for up to this long
_POLL_INTERVAL: t.Final = 0.05

CallbackPage = t.Callable[[t.Mapping[str, str]], str]


def render_callback_page(params: t.Mapping[str, str]) -> str:
    """Render the default page: one fixed message for a success and another for a failure."""
    return _PAGE.format(_FAILURE_MESSAGE if 'error' in params else _SUCCESS_MESSAGE)


class _Server(ThreadingHTTPServer):
    def __init__(self, address: t.Tuple[str, int], callback_path: str, page: CallbackPage) -> None:
        if ':' in address[0]:
            self.address_family = socket.AF_INET6

        super().__init__(address, _Handler)
        self.callback_path = callback_path
        self.page = page
        self.params: t.Optional[t.Dict[str, str]] = None
        self.page_error: t.Optional[Exception] = None
        self.received = threading.Event()

    @te.override
    def server_bind(self) -> None:
        # the base class also looks up the name of the host, which takes seconds on some systems
        socketserver.TCPServer.server_bind(self)
        self.server_name = str(self.server_address[0])
        self.server_port = self.server_address[1]


class _Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        server = t.cast('_Server', self.server)

        url = urlsplit(self.path)
        if url.path != server.callback_path or server.received.is_set():
            self.send_error(404)
            return

        server.params = dict(parse_qsl(url.query))
        try:
            self._send_page(server.page(server.params))
        except Exception as e:  # noqa: BLE001
            # raised to the caller of wait(), who passed the page
            server.page_error = e
            self.send_error(500)
        finally:
            server.received.set()

    def _send_page(self, page: str) -> None:
        body = page.encode('UTF-8')

        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    @te.override
    def log_message(self, format: str, *args: t.Any) -> None:
        pass


class LoopbackCallbackServer:
    """Local HTTP server that receives the redirect back from the authorization server.

    Pass :py:attr:`redirect_uri` to ``authorize`` and the result of :py:meth:`wait` to ``callback``.

    Args:
        redirect_uris: Redirect URIs of the client. The first loopback one is served;
            without a port in it, the system picks a free one.
        page: Returns the HTML shown in the browser, given the query parameters of the redirect.
            The parameters come from the network, so escape any of them the page includes.
            The page is sent before the authorization is completed with ``callback``.

    Attributes:
        redirect_uri: Redirect URI the server listens on.

    Raises:
        :class:`ValueError`: None of the redirect URIs is a loopback one.
    """

    def __init__(self, redirect_uris: t.Sequence[str], page: t.Optional[CallbackPage] = None) -> None:
        registered = next((uri for uri in redirect_uris if is_loopback_redirect_uri(uri)), None)
        if registered is None:
            raise ValueError('The client has no redirect URI on 127.0.0.1 or [::1]')

        parts = urlsplit(registered)
        hostname = parts.hostname or ''
        self._server = _Server((hostname, parts.port or 0), parts.path or '/', page or render_callback_page)

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

        Args:
            timeout: Seconds to wait. :obj:`None` waits forever.

        Raises:
            :class:`atproto_oauth.exceptions.OAuthCallbackError`: Nothing arrived in time.
        """
        self._server.received.wait(timeout)
        if self._server.page_error is not None:
            raise self._server.page_error

        if self._server.params is None:
            raise OAuthCallbackError('The authorization was not completed in time')

        return self._server.params

    def close(self) -> None:
        """Stop the server."""
        # a cancelled login leaves a thread waiting for the redirect
        self._server.received.set()
        self._server.shutdown()
        self._server.server_close()
        self._thread.join()


def login_flow(
    client: t.Any,
    identifier: str,
    open_url: t.Callable[[str], t.Any],
    page: t.Optional[CallbackPage],
    timeout: t.Optional[float],
    params: t.Mapping[str, t.Any],
) -> Flow[t.Any]:
    with LoopbackCallbackServer(client.client_metadata['redirect_uris'], page) as server:
        url = yield call(client.authorize, identifier, redirect_uri=server.redirect_uri, **params)
        open_url(url)

        callback_params = yield call_blocking(server.wait, timeout)
        result = yield call(client.callback, callback_params)

    return result.session

import json
import typing as t
from dataclasses import dataclass

import httpx

from atproto import exceptions
from atproto.xrpc_client.models.common import XrpcError
from atproto.xrpc_client.models.utils import get_or_create, is_json


@dataclass
class Response:
    success: bool
    status_code: int
    content: t.Optional[t.Union[dict, bytes, 'XrpcError']]
    headers: t.Dict[str, t.Any]


def _parse_response(response: httpx.Response) -> Response:
    content = response.content
    if response.headers.get('content-type') == 'application/json; charset=utf-8':
        content = response.json()

    return Response(
        success=True,
        status_code=response.status_code,
        content=content,
        headers=response.headers,
    )


def _handle_request_errors(exception: Exception) -> None:
    try:
        raise exception
    except httpx.TimeoutException as e:
        raise exceptions.InvokeTimeoutError from e
    except httpx.NetworkError as e:
        raise exceptions.NetworkError from e
    # TODO(MarshalX): add more exceptions


def _handle_response(response: httpx.Response) -> httpx.Response:
    if 200 <= response.status_code <= 299:
        return response

    error_response = Response(
        success=False,
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
    )
    if response.content and is_json(response.content):
        data = json.loads(response.content)
        error_response.content = get_or_create(data, XrpcError)

    if response.status_code in {401, 403}:
        raise exceptions.UnauthorizedError(error_response)
    if response.status_code == 400:
        raise exceptions.BadRequestError(error_response)
    if response.status_code in {409, 413, 502}:
        raise exceptions.NetworkError(error_response)

    raise exceptions.RequestException(error_response)


class RequestBase:
    _MANDATORY_HEADERS: t.ClassVar[t.Dict[str, str]] = {'User-Agent': 'atproto/alpha (Python SDK)'}

    def __init__(self) -> None:
        self._additional_headers: dict = {}

    def get_headers(self, additional_headers: t.Optional[dict] = None) -> dict:
        headers = {**RequestBase._MANDATORY_HEADERS, **self._additional_headers}

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def set_additional_headers(self, headers: dict) -> None:
        if isinstance(headers, dict):
            self._additional_headers = headers.copy()
        else:
            raise ValueError('Headers must be dict')


class Request(RequestBase):
    """Class for handling requests errors and working with httpx"""

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.Client()

    def _send_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        headers = self.get_headers(kwargs.pop('headers', None))

        try:
            response = self._client.request(method=method, url=url, headers=headers, **kwargs)
            return _handle_response(response)
        except Exception as e:
            _handle_request_errors(e)
            raise e

    def close(self) -> None:
        self._client.close()

    def get(self, *args, **kwargs) -> Response:
        return _parse_response(self._send_request('GET', *args, **kwargs))

    def post(self, *args, **kwargs) -> Response:
        return _parse_response(self._send_request('POST', *args, **kwargs))


class AsyncRequest(RequestBase):
    """Class for handling requests errors and working with httpx"""

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.AsyncClient()

    async def _send_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        headers = self.get_headers(kwargs.pop('headers', None))

        try:
            response = await self._client.request(method=method, url=url, headers=headers, **kwargs)
            return _handle_response(response)
        except Exception as e:
            _handle_request_errors(e)
            raise e

    async def close(self) -> None:
        await self._client.aclose()

    async def get(self, *args, **kwargs) -> Response:
        return _parse_response(await self._send_request('GET', *args, **kwargs))

    async def post(self, *args, **kwargs) -> Response:
        return _parse_response(await self._send_request('POST', *args, **kwargs))

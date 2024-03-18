import json
import typing as t
from dataclasses import dataclass

import httpx

from atproto_client import exceptions
from atproto_client.models.common import XrpcError
from atproto_client.models.utils import get_or_create, is_json


@dataclass
class Response:
    success: bool
    status_code: int
    content: t.Optional[t.Union[t.Dict[str, t.Any], bytes, 'XrpcError']]
    headers: t.Dict[str, t.Any]


def _convert_headers_to_dict(headers: httpx.Headers) -> t.Dict[str, str]:
    headers_dict: t.Dict[str, str] = {}

    for key, value in headers.raw:
        str_key = key.decode(headers.encoding)
        str_value = value.decode(headers.encoding)
        if str_key in headers_dict:
            headers_dict[str_key] += f', {str_value}'
        else:
            headers_dict[str_key] = str_value

    return headers_dict


def _parse_response(response: httpx.Response) -> Response:
    content = response.content
    if response.headers.get('content-type') == 'application/json; charset=utf-8':
        content = response.json()

    return Response(
        success=True,
        status_code=response.status_code,
        content=content,
        headers=_convert_headers_to_dict(response.headers),
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
        headers=_convert_headers_to_dict(response.headers),
    )
    if response.content and is_json(response.content):
        data: t.Dict[str, t.Any] = json.loads(response.content)
        error_response.content = t.cast(XrpcError, get_or_create(data, XrpcError))

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
        self._additional_headers: t.Dict[str, str] = {}

    def get_headers(self, additional_headers: t.Optional[t.Dict[str, str]] = None) -> t.Dict[str, str]:
        headers = {**RequestBase._MANDATORY_HEADERS, **self._additional_headers}

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def set_additional_headers(self, headers: t.Dict[str, str]) -> None:
        self._additional_headers = headers.copy()


class Request(RequestBase):
    """Class for handling requests errors and working with httpx."""

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.Client(follow_redirects=True)

    def _send_request(self, method: str, url: str, **kwargs: t.Any) -> httpx.Response:
        headers = self.get_headers(kwargs.pop('headers', None))

        try:
            response = self._client.request(method=method, url=url, headers=headers, **kwargs)
            return _handle_response(response)
        except Exception as e:
            _handle_request_errors(e)
            raise e

    def close(self) -> None:
        self._client.close()

    def get(self, *args: t.Any, **kwargs: t.Any) -> Response:
        return _parse_response(self._send_request('GET', *args, **kwargs))

    def post(self, *args: t.Any, **kwargs: t.Any) -> Response:
        return _parse_response(self._send_request('POST', *args, **kwargs))


class AsyncRequest(RequestBase):
    """Class for handling requests errors and working with httpx."""

    def __init__(self) -> None:
        super().__init__()
        self._client = httpx.AsyncClient(follow_redirects=True)

    async def _send_request(self, method: str, url: str, **kwargs: t.Any) -> httpx.Response:
        headers = self.get_headers(kwargs.pop('headers', None))

        try:
            response = await self._client.request(method=method, url=url, headers=headers, **kwargs)
            return _handle_response(response)
        except Exception as e:
            _handle_request_errors(e)
            raise e

    async def close(self) -> None:
        await self._client.aclose()

    async def get(self, *args: t.Any, **kwargs: t.Any) -> Response:
        return _parse_response(await self._send_request('GET', *args, **kwargs))

    async def post(self, *args: t.Any, **kwargs: t.Any) -> Response:
        return _parse_response(await self._send_request('POST', *args, **kwargs))

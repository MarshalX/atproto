from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

import httpx

from atproto import exceptions


@dataclass
class Response:
    status_code: int
    headers: Dict[str, Any]
    content: Optional[Union[dict, bytes]]


def _parse_response(response: httpx.Response) -> Response:
    content = response.content
    if response.headers.get('content-type') == 'application/json; charset=utf-8':
        content = response.json()

    return Response(status_code=response.status_code, headers=response.headers, content=content)


def _handle_request_errors(exception: Exception) -> None:
    try:
        raise exception
    except httpx.TimeoutException:
        raise exceptions.InvokeTimeoutError()
    except httpx.NetworkError:
        raise exceptions.NetworkError()
    except Exception as e:
        raise exceptions.RequestException from e


def _handle_response(response: httpx.Response) -> httpx.Response:
    if 200 <= response.status_code <= 299:
        return response

    if response.status_code in {401, 403}:
        raise exceptions.UnauthorizedError(response)
    elif response.status_code == 404:
        raise exceptions.BadRequestError()
    elif response.status_code in {409, 413}:
        raise exceptions.NetworkError()
    elif response.status_code == 502:
        raise exceptions.NetworkError('Bad Gateway')
    else:
        raise exceptions.RequestException(response)


class RequestBase:
    MANDATORY_HEADERS = {'User-Agent': f'atproto/alpha (Python SDK)'}

    def __init__(self):
        self._additional_headers: dict = {}

    def get_headers(self, additional_headers: Optional[dict] = None) -> dict:
        headers = {**self.MANDATORY_HEADERS, **self._additional_headers}

        if additional_headers:
            headers.update(additional_headers)

        return headers

    def set_additional_headers(self, headers: dict) -> None:
        if isinstance(headers, dict):
            self._additional_headers = headers.copy()
        else:
            raise ValueError('Headers should be dict!')


class Request(RequestBase):
    """Class for handling requests errors and working with httpx"""

    def __init__(self):
        super().__init__()
        self._client = httpx.Client()

    def _send_request(self, method: str, url: str, *args, **kwargs) -> httpx.Response:
        headers = self.get_headers(kwargs.get('headers'))

        try:
            response = self._client.request(method=method, url=url, headers=headers, *args, **kwargs)
            return _handle_response(response)
        except Exception as e:
            _handle_request_errors(e)

    def close(self):
        self._client.close()

    def get(self, *args, **kwargs) -> Response:
        return _parse_response(self._send_request('GET', *args, **kwargs))

    def post(self, *args, **kwargs) -> Response:
        return _parse_response(self._send_request('POST', *args, **kwargs))


class AsyncRequest(RequestBase):
    """Class for handling requests errors and working with httpx"""

    def __init__(self):
        super().__init__()
        self._client = httpx.AsyncClient()

    async def _send_request(self, method: str, url: str, *args, **kwargs) -> httpx.Response:
        headers = self.get_headers(kwargs.get('headers'))

        try:
            response = await self._client.request(method=method, url=url, headers=headers, *args, **kwargs)
            return _handle_response(response)
        except Exception as e:
            _handle_request_errors(e)

    async def close(self):
        await self._client.aclose()

    async def get(self, *args, **kwargs) -> Response:
        return _parse_response(await self._send_request('GET', *args, **kwargs))

    async def post(self, *args, **kwargs) -> Response:
        return _parse_response(await self._send_request('POST', *args, **kwargs))

import typing as t
from enum import Enum

from atproto.xrpc_client.models.utils import get_model_as_dict, get_model_as_json
from atproto.xrpc_client.request import AsyncRequest, Request, Response

if t.TYPE_CHECKING:
    from atproto.xrpc_client.models.base import DataModelBase, ParamsModelBase

# TODO(MarshalX): Generate async version automatically!


class InvokeType(Enum):
    QUERY = 'query'
    PROCEDURE = 'procedure'


_BASE_API_URL = 'https://bsky.social/xrpc'

_CONTENT_TYPE_JSON = 'application/json'
_DEFAULT_CONTENT_TYPE = _CONTENT_TYPE_JSON


def _handle_kwagrs(kwargs: dict) -> None:
    """Mutates input data"""
    content_type = _DEFAULT_CONTENT_TYPE

    if 'headers' not in kwargs:
        kwargs['headers'] = {}

    if 'input_encoding' in kwargs:
        content_type = kwargs['input_encoding']

    kwargs['headers'].update({'Content-Type': content_type})

    if content_type == _CONTENT_TYPE_JSON and 'data' in kwargs and kwargs['data']:
        kwargs['data'] = get_model_as_json(kwargs['data'])

    if 'params' in kwargs and kwargs['params']:
        kwargs['params'] = get_model_as_dict(kwargs['params'])

    # pop non-request kwargs
    kwargs.pop('input_encoding', None)
    kwargs.pop('output_encoding', None)


class ClientBase:
    """Low-level methods are here"""

    def __init__(self, base_url: t.Optional[str] = None, request: t.Optional[Request] = None) -> None:
        if request is None:
            request = Request()
        if base_url is None:
            base_url = _BASE_API_URL

        self._request = request
        self._base_url = base_url

    @property
    def request(self) -> Request:
        return self._request

    def _build_url(self, nsid: str) -> str:
        return f'{self._base_url}/{nsid}'

    def invoke_query(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs,
    ) -> Response:
        return self._invoke(InvokeType.QUERY, url=self._build_url(nsid), params=params, data=data, **kwargs)

    def invoke_procedure(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs,
    ) -> Response:
        return self._invoke(InvokeType.PROCEDURE, url=self._build_url(nsid), params=params, data=data, **kwargs)

    def _invoke(self, invoke_type: InvokeType, **kwargs) -> Response:
        _handle_kwagrs(kwargs)

        if invoke_type is InvokeType.QUERY:
            return self.request.get(**kwargs)
        return self.request.post(**kwargs)


class AsyncClientBase:
    """Low-level methods are here"""

    def __init__(self, base_url: t.Optional[str] = None, request: t.Optional[AsyncRequest] = None) -> None:
        if request is None:
            request = AsyncRequest()
        if base_url is None:
            base_url = _BASE_API_URL

        self._request = request
        self._base_url = base_url

    @property
    def request(self) -> AsyncRequest:
        return self._request

    def _build_url(self, nsid: str) -> str:
        return f'{self._base_url}/{nsid}'

    async def invoke_query(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs,
    ) -> Response:
        return await self._invoke(InvokeType.QUERY, url=self._build_url(nsid), params=params, data=data, **kwargs)

    async def invoke_procedure(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs,
    ) -> Response:
        return await self._invoke(InvokeType.PROCEDURE, url=self._build_url(nsid), params=params, data=data, **kwargs)

    async def _invoke(self, invoke_type: InvokeType, **kwargs) -> Response:
        _handle_kwagrs(kwargs)

        if invoke_type is InvokeType.QUERY:
            return await self.request.get(**kwargs)
        return await self.request.post(**kwargs)

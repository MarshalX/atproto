import typing as t

if t.TYPE_CHECKING:
    from atproto_client.models.base import DataModelBase, ParamsModelBase
    from atproto_client.request import Response


@t.runtime_checkable
class XrpcClient(t.Protocol):
    """Client that invokes XRPC methods."""

    def invoke_query(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs: t.Any,
    ) -> 'Response': ...

    def invoke_procedure(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs: t.Any,
    ) -> 'Response': ...


@t.runtime_checkable
class AsyncXrpcClient(t.Protocol):
    """Client that awaits XRPC methods."""

    async def invoke_query(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs: t.Any,
    ) -> 'Response': ...

    async def invoke_procedure(
        self,
        nsid: str,
        params: t.Optional['ParamsModelBase'] = None,
        data: t.Optional[t.Union['DataModelBase', bytes]] = None,
        **kwargs: t.Any,
    ) -> 'Response': ...


class NamespaceBase:
    def __init__(self, client: 'XrpcClient') -> None:
        self._client: XrpcClient = client


class AsyncNamespaceBase:
    def __init__(self, client: 'AsyncXrpcClient') -> None:
        self._client: AsyncXrpcClient = client


class RecordBase:
    def __init__(self, client: 'XrpcClient') -> None:
        self._client: XrpcClient = client


class AsyncRecordBase:
    def __init__(self, client: 'AsyncXrpcClient') -> None:
        self._client: AsyncXrpcClient = client

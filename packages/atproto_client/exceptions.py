import typing as t

from atproto_core.exceptions import AtProtocolError

if t.TYPE_CHECKING:
    from atproto_client.request import Response


class ModelError(AtProtocolError):
    ...


class ModelFieldNotFoundError(ModelError):
    ...


class RequestErrorBase(AtProtocolError):
    def __init__(self, response: t.Optional['Response'] = None) -> None:
        self.response: t.Optional['Response'] = response


class NetworkError(RequestErrorBase):
    ...


class InvokeTimeoutError(NetworkError):
    ...


class UnauthorizedError(RequestErrorBase):
    ...


class RequestException(RequestErrorBase):
    ...


class BadRequestError(RequestErrorBase):
    ...

import typing as t

if t.TYPE_CHECKING:
    from atproto.xrpc_client.request import Response


class AtProtocolError(Exception):
    """Base exception"""


class LexiconParsingError(AtProtocolError):
    ...


class UnknownPrimitiveTypeError(LexiconParsingError):
    ...


class UnknownDefinitionTypeError(LexiconParsingError):
    ...


class InvalidNsidError(AtProtocolError):
    ...


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


class InvalidAtUriError(AtProtocolError):
    ...


class FirehoseError(AtProtocolError):
    ...


class FirehoseDecodingError(FirehoseError):
    ...


class DAGCBORDecodingError(AtProtocolError):
    ...


class InvalidCARFile(AtProtocolError):
    ...

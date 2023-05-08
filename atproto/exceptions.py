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


class UnexpectedFieldError(ModelError):
    ...


class MissingValueError(ModelError):
    ...


class ModelFieldError(ModelError):
    ...


class WrongTypeError(ModelFieldError):
    ...


class ModelFieldNotFoundError(ModelError):
    ...


class NetworkError(AtProtocolError):
    ...


class InvokeTimeoutError(NetworkError):
    ...


class UnauthorizedError(AtProtocolError):
    def __init__(self, response):
        self.response = response


class RequestException(AtProtocolError):
    ...


class BadRequestError(RequestException):
    ...


class InvalidAtUriError(AtProtocolError):
    ...

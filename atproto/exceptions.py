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

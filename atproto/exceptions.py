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

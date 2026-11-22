class AtProtocolError(Exception):
    """Base exception."""


class InvalidNsidError(AtProtocolError): ...


class InvalidAtUriError(AtProtocolError): ...


class InvalidCARFile(AtProtocolError): ...


class InvalidStarError(AtProtocolError): ...


class DAGCBORDecodingError(AtProtocolError): ...


class DAGCBOREncodingError(AtProtocolError): ...

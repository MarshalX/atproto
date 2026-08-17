from atproto_core.exceptions import AtProtocolError


class JetstreamError(AtProtocolError): ...


class JetstreamDecodingError(JetstreamError): ...


class JetstreamConsumerTooSlowError(JetstreamError):
    """The server dropped the connection because the client fell too far behind."""


class JetstreamCursorTooOldError(JetstreamError):
    """The requested cursor is below the server's retention floor."""

from atproto_core.exceptions import AtProtocolError


class DidPlcResolverError(AtProtocolError):
    ...


class DidWebResolverError(AtProtocolError):
    ...


class PoorlyFormattedDidError(AtProtocolError):
    ...


class UnsupportedDidWebPathError(AtProtocolError):
    ...


class UnsupportedDidMethodError(AtProtocolError):
    ...


class PoorlyFormattedDidDocumentError(AtProtocolError):
    ...


class DidNotFoundError(AtProtocolError):
    ...

from atproto_core.exceptions import AtProtocolError


class SubscriptionError(AtProtocolError):
    """Base exception of the subscription runtime."""


class FrameDecodingError(SubscriptionError):
    """Frame could not be decoded."""

"""Aliases of the subscription runtime's exceptions, kept for backward compatibility."""

from atproto_subscription.exceptions import FrameDecodingError, SubscriptionError

FirehoseError = SubscriptionError
FirehoseDecodingError = FrameDecodingError

__all__ = ['FirehoseDecodingError', 'FirehoseError']

"""Moved to :mod:`atproto_subscription.client`. Kept importable for backward compatibility."""

from atproto_subscription.client import AsyncSubscriptionClient, SubscriptionClient

FirehoseClient = SubscriptionClient
AsyncFirehoseClient = AsyncSubscriptionClient

__all__ = ['AsyncFirehoseClient', 'FirehoseClient']

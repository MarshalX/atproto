"""The modules whose contents moved into :mod:`atproto_subscription` stay importable, with a warning."""

import warnings

import pytest


@pytest.mark.parametrize(
    ('module', 'name', 'target'),
    [
        ('atproto_core.websocket', 'WebsocketClient', 'atproto_subscription.websocket.WebsocketClient'),
        ('atproto_core.websocket', 'AsyncWebsocketClient', 'atproto_subscription.websocket.AsyncWebsocketClient'),
        ('atproto_core.websocket', 'build_websocket_uri', 'atproto_subscription.websocket.build_websocket_uri'),
        ('atproto_firehose.client', 'FirehoseClient', 'atproto_subscription.client.SubscriptionClient'),
        ('atproto_firehose.client', 'AsyncFirehoseClient', 'atproto_subscription.client.AsyncSubscriptionClient'),
    ],
)
def test_moved_name_warns_and_still_resolves(module: str, name: str, target: str) -> None:
    import importlib

    imported = importlib.import_module(module)

    with pytest.warns(DeprecationWarning, match=target.replace('.', r'\.')):
        value = getattr(imported, name)

    module_path, _, attribute = target.rpartition('.')
    assert value is getattr(importlib.import_module(module_path), attribute)


@pytest.mark.parametrize('module', ['atproto_core.websocket', 'atproto_firehose.client'])
def test_unknown_name_still_raises_attribute_error(module: str) -> None:
    import importlib

    with pytest.raises(AttributeError):
        importlib.import_module(module).does_not_exist  # noqa: B018


def test_importing_the_sdk_does_not_warn() -> None:
    """Nothing inside the SDK may route through the deprecated shims."""
    import importlib

    with warnings.catch_warnings():
        warnings.simplefilter('error', DeprecationWarning)
        importlib.reload(importlib.import_module('atproto_firehose.firehose'))
        importlib.reload(importlib.import_module('atproto_jetstream.client'))

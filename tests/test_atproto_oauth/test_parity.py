import inspect
import typing as t

import pytest
from atproto_oauth import (
    AsyncOAuthClient,
    AsyncOAuthResolver,
    AsyncOAuthSession,
    OAuthClient,
    OAuthResolver,
    OAuthSession,
)


def _public_api(cls: type) -> t.Dict[str, t.List[str]]:
    api: t.Dict[str, t.List[str]] = {}
    for name, member in inspect.getmembers(cls):
        if name.startswith('_'):
            continue

        if isinstance(inspect.getattr_static(cls, name), property):
            api[name] = ['<property>']
        elif callable(member):
            api[name] = list(inspect.signature(member).parameters)

    return api


def _init_parameters(cls: type) -> t.List[str]:
    return list(inspect.signature(cls).parameters)


@pytest.mark.parametrize(
    ('sync_cls', 'async_cls'),
    [
        (OAuthClient, AsyncOAuthClient),
        (OAuthSession, AsyncOAuthSession),
        (OAuthResolver, AsyncOAuthResolver),
    ],
)
def test_sync_and_async_classes_have_the_same_api(sync_cls: type, async_cls: type) -> None:
    assert _public_api(sync_cls) == _public_api(async_cls)

    assert _init_parameters(sync_cls) == _init_parameters(async_cls)


@pytest.mark.parametrize('cls', [AsyncOAuthClient, AsyncOAuthSession, AsyncOAuthResolver])
def test_async_classes_have_coroutine_methods(cls: type) -> None:
    sync_cls = {
        'AsyncOAuthClient': OAuthClient,
        'AsyncOAuthSession': OAuthSession,
        'AsyncOAuthResolver': OAuthResolver,
    }[cls.__name__]
    declared_in_sync = {name for name, member in vars(sync_cls).items() if inspect.isfunction(member)}

    for name, member in vars(cls).items():
        if name in declared_in_sync and not name.startswith('_') and inspect.isfunction(member):
            assert inspect.iscoroutinefunction(member), name

import inspect
import typing as t

import pytest
from atproto_space import (
    AsyncSpaceClient,
    AsyncSpaceManager,
    AsyncSpaceReader,
    SpaceClient,
    SpaceManager,
    SpaceReader,
)
from atproto_space.async_client import _AsyncClientOptions
from atproto_space.client import _ClientOptions

_PAIRS = [
    (SpaceReader, AsyncSpaceReader),
    (SpaceClient, AsyncSpaceClient),
    (SpaceManager, AsyncSpaceManager),
]

_Parameter = t.Tuple[str, object, object]


def _parameters(func: t.Callable[..., object]) -> t.List[_Parameter]:
    return [
        (parameter.name, parameter.kind, parameter.default) for parameter in inspect.signature(func).parameters.values()
    ]


def _public_methods(cls: type) -> t.Dict[str, t.Callable[..., object]]:
    return {
        name: member
        for name, member in inspect.getmembers(cls, callable)
        if not name.startswith('_') and not isinstance(inspect.getattr_static(cls, name), property)
    }


def _public_properties(cls: type) -> t.List[str]:
    return [
        name
        for name, _ in inspect.getmembers(cls)
        if not name.startswith('_') and isinstance(inspect.getattr_static(cls, name), property)
    ]


@pytest.mark.parametrize(('sync_cls', 'async_cls'), _PAIRS)
def test_sync_and_async_classes_have_the_same_api(sync_cls: type, async_cls: type) -> None:
    sync_methods = _public_methods(sync_cls)
    async_methods = _public_methods(async_cls)

    assert list(sync_methods) == list(async_methods)
    assert _public_properties(sync_cls) == _public_properties(async_cls)
    assert _parameters(sync_cls) == _parameters(async_cls)
    for name, method in sync_methods.items():
        assert _parameters(method) == _parameters(async_methods[name]), name


@pytest.mark.parametrize(('sync_cls', 'async_cls'), _PAIRS)
def test_methods_of_async_classes_are_asynchronous(sync_cls: type, async_cls: type) -> None:
    sync_methods = _public_methods(sync_cls)

    for name, method in _public_methods(async_cls).items():
        if inspect.isgeneratorfunction(sync_methods[name]):
            assert inspect.isasyncgenfunction(method), name
        else:
            assert inspect.iscoroutinefunction(method), name


@pytest.mark.parametrize('cls', [sync_cls for sync_cls, _ in _PAIRS])
def test_methods_of_sync_classes_are_synchronous(cls: type) -> None:
    for name, method in _public_methods(cls).items():
        assert not inspect.iscoroutinefunction(method), name
        assert not inspect.isasyncgenfunction(method), name


@pytest.mark.parametrize(
    ('cls', 'options'),
    [(SpaceClient, _ClientOptions), (AsyncSpaceClient, _AsyncClientOptions)],
)
def test_constructor_options_match_the_client_arguments(cls: type, options: type) -> None:
    arguments = [name for name, kind, _ in _parameters(cls) if kind is inspect.Parameter.KEYWORD_ONLY]

    assert list(options.__annotations__) == arguments

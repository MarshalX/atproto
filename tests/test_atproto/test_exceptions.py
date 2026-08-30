import importlib
import importlib.util
import inspect
import pkgutil
import typing as t

import atproto
import atproto.exceptions
import pytest


def _exception_modules() -> t.List[str]:
    """Every ``atproto_*.exceptions`` module that ships with the SDK."""
    packages = [
        module.name
        for module in pkgutil.iter_modules()
        if module.ispkg and module.name.startswith('atproto_') and not module.name.endswith(('_cli', '_codegen'))
    ]

    return [f'{package}.exceptions' for package in packages if importlib.util.find_spec(f'{package}.exceptions')]


@pytest.mark.parametrize('module_name', _exception_modules())
def test_every_exception_is_re_exported(module_name: str) -> None:
    module = importlib.import_module(module_name)

    for name, value in vars(module).items():
        if name.startswith('_') or not inspect.isclass(value) or not issubclass(value, BaseException):
            continue

        assert getattr(atproto.exceptions, name, None) is value, f'{module_name}.{name} is not in atproto.exceptions'


def test_jetstream_exceptions_are_re_exported() -> None:
    from atproto_jetstream.exceptions import JetstreamCursorTooOldError

    assert atproto.exceptions.JetstreamCursorTooOldError is JetstreamCursorTooOldError

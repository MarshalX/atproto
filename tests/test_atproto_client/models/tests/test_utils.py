import pytest
from atproto_client.models.utils import is_json, load_json


def test_load_json() -> None:
    assert load_json('{"key": "value"}')
    assert load_json(b'{"key": "value"}')

    assert load_json('{"key": "value"', strict=False) is None
    with pytest.raises(ValueError):
        load_json(b'{"key": "value"')

    assert load_json('{"key": "value"', strict=False) is None
    with pytest.raises(ValueError):
        load_json(b'{"key": "value"')

    assert load_json('{"key": "value"}'.encode('UTF-16'), strict=False) is None

    with pytest.raises(TypeError):
        load_json(None)


def test_is_json() -> None:
    assert is_json('{"key": "value"}') is True
    assert is_json(b'{"key": "value"}') is True

    assert is_json('{"key": "value"') is False
    assert is_json(b'{"key": "value"') is False

    assert is_json('{"key": "value"}'.encode('UTF-16')) is False

    assert is_json(b'') is False
    assert is_json(b'{}') is True

    with pytest.raises(TypeError):
        load_json(None)

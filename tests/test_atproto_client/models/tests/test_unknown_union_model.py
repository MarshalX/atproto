import pytest
from atproto_client.models.base import UnknownUnionModel
from pydantic import ValidationError


def test_unknown_union_model() -> None:
    """Test the UnknownUnionModel class."""
    expected_type = 'app.bsky.embed.record#view'

    model = UnknownUnionModel(py_type=expected_type)
    assert model.py_type == expected_type

    with pytest.raises(ValidationError):
        # Attempt to create an instance without $type
        UnknownUnionModel(blabla='blabla')

    model = UnknownUnionModel.model_validate_json(f'{{"$type": "{expected_type}"}}')
    assert model.py_type == expected_type

    with pytest.raises(ValidationError):
        # Attempt to create an instance without $type
        UnknownUnionModel.model_validate_json('{"literallyNoTypeInfo": "lol"}')

    model_with_extra = UnknownUnionModel(py_type=expected_type, extra_field='extra_value')
    assert model_with_extra.extra_field == 'extra_value'

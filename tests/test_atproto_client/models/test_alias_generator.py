from atproto_client.models.base import ModelBase, _alias_generator
from atproto_client.models.utils import get_model_as_dict


def test_alias_generator() -> None:
    assert _alias_generator('test_field') == 'testField'
    assert _alias_generator('test_field_') == 'testField'


class TestModel(ModelBase):
    test_field: str
    validate_: bool  # with underscore because collide with pydantic's "validate" method


def test_model_base_aliases() -> None:
    model = TestModel(testField='test', validate=True)
    assert model.test_field == 'test'
    assert model.validate_ is True

    plain_model = get_model_as_dict(model)
    assert plain_model['testField'] == 'test'
    assert plain_model['validate'] is True

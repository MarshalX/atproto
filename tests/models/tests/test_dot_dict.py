from atproto.xrpc_client.models.dot_dict import DotDict


def test_dot_dict():
    test_data = {'a': 1, 'b': {'c': 2}, 'd': [{'e': 3}, 4, 5]}
    model = DotDict(test_data)

    assert isinstance(model, DotDict)

    assert model.nonExistingField is None

    assert model.a == 1
    assert model['a'] == 1

    assert model['b']['c'] == 2
    assert model.b.c == 2
    assert model.b['c'] == 2
    assert model['b'].c == 2

    assert model.d[0].e == 3
    assert model['d'][0]['e'] == 3
    assert model['d'][0].e == 3

    assert model['d'][1] == 4
    assert model['d'][2] == 5

    model['d'][0]['e'] = 6
    assert model['d'][0]['e'] == 6

    assert DotDict(test_data) == DotDict(test_data)
    assert model.to_dict() == test_data

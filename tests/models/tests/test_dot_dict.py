from atproto.xrpc_client.models.dot_dict import DotDict


def test_dot_dict() -> None:
    expected_created_at = '2021-03-30T12:00:00Z'
    expected_snake_case = 'test'

    test_data = {
        'a': 1,
        'b': {'c': 2},
        'd': [{'e': 3}, 4, 5],
        'createdAt': expected_created_at,
        'snake_case': expected_snake_case,
    }
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

    assert model.createdAt == expected_created_at
    assert model['createdAt'] == expected_created_at
    assert model.created_at == expected_created_at
    assert model['created_at'] == expected_created_at

    expected_created_at = 'pupu'
    model.createdAt = expected_created_at
    assert model.createdAt == expected_created_at
    assert model.created_at == expected_created_at

    expected_created_at = 'blabla'
    model.created_at = expected_created_at
    assert model.created_at == expected_created_at
    assert model.createdAt == expected_created_at

    assert model.snake_case == expected_snake_case
    assert model['snake_case'] == expected_snake_case
    assert model.snakeCase == expected_snake_case
    assert model['snakeCase'] == expected_snake_case

    assert DotDict(test_data) == DotDict(test_data)
    assert model.to_dict() == test_data

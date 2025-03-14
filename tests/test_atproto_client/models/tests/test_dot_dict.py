from atproto_client.models.dot_dict import DotDict


def test_dot_dict_input_mutation() -> None:
    test_data = {'a': 1, 'b': {'c': 2}, 'd': [{'e': 3}, 4, 5]}
    model = DotDict(test_data)

    model['a'] = 2
    assert model['a'] == 2
    assert test_data['a'] == 1

    model.b.c = 3
    assert model.b.c == 3
    assert test_data['b']['c'] == 2

    model['d'][0]['e'] = 6
    assert model['d'][0]['e'] == 6
    assert test_data['d'][0]['e'] == 3


def test_dot_dict_output_mutation() -> None:
    model = DotDict({'a': 1, 'b': {'c': 2}, 'd': [{'e': 3}, 4, 5]})
    output_dict = model.to_dict()

    output_dict['a'] = 2
    assert model['a'] == 1

    output_dict['b']['c'] = 3
    assert model.b.c == 2

    output_dict['d'][0]['e'] = 6
    assert model['d'][0]['e'] == 3


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
    expected_edited_test_data = {
        'a': 1,
        'b': {'c': 2},
        'createdAt': 'blabla',
        'd': [{'e': 6}, 4, 5],
        'snake_case': 'test',
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

    assert isinstance(model.to_dict(), dict)
    assert model.to_dict() == expected_edited_test_data
    assert model.to_dict() == model.to_dict()

    dict_model = model.to_dict()
    assert dict_model['a'] == 1
    assert dict_model['d'][0]['e'] == 6
    assert dict_model['createdAt'] == 'blabla'


def test_dot_dict_iter() -> None:
    test_data = {'a': 1, 'b': {'c': 2}, 'd': [{'e': 3}]}
    model = DotDict(test_data)

    # Test list conversion
    keys_list = list(model)
    assert keys_list == list(test_data)
    assert isinstance(keys_list, list)

    # Test looping
    og_iter = iter(test_data)
    for key in model:
        assert key == next(og_iter)


def test_dot_dict_mapping_protocol() -> None:
    test_data = {'a': 1, 'b': {'c': 2}, 'd': [{'e': 3}]}
    model = DotDict(test_data)

    # Test dict conversion
    converted_dict = dict(model)
    assert converted_dict == test_data
    assert converted_dict is not test_data
    assert isinstance(converted_dict, dict)
    assert not isinstance(converted_dict, DotDict)

    # Test keys looping
    og_iter = iter(test_data.keys())
    for key in model:
        assert key == next(og_iter)

    # Test values looping
    og_iter = iter(test_data.values())
    for value in model.values():
        assert value == next(og_iter)

    # Test items looping
    og_iter = iter(test_data.items())
    for key, value in model.items():
        next_item = next(og_iter)
        assert key == next_item[0]
        assert value == next_item[1]

    # Test len
    assert len(model) == len(test_data)
    assert len(DotDict({})) == 0

    # Test contains
    assert 'a' in model
    assert 'b' in model
    assert 'c' not in model

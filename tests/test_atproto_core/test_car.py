from atproto_core.car import CAR


def test_car() -> None:
    car_bytes = '3aa265726f6f747381d82a582500017112206952534c9d447cf8e0e924ac646a036a3769b3eb755c11adba872e78cec29f916776657273696f6e01b5'  # noqa: E501
    expected_root = 'bafyreidjkjjuzhkept4ob2jevrsgua3kg5u3h23vlqi23ouhfz4m5qu7se'

    car = CAR.from_bytes(bytes.fromhex(car_bytes))
    assert expected_root == car.root
    assert len(car.blocks) == 0

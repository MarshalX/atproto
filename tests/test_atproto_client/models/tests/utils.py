import os

from pydantic_core import from_json

TEST_DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'test_data')


def load_data_from_file(test_name: str) -> dict:
    with open(os.path.join(TEST_DATA_PATH, f'{test_name}.json'), encoding='UTF-8') as f:
        return from_json(f.read())

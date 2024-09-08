import base64
import os

import pytest
from atproto_crypto.verify import verify_signature
from pydantic_core import from_json

# Ref: https://github.com/bluesky-social/atproto/blob/main/interop-test-files/crypto/signature-fixtures.json
_FIXTURES_FILE_PATH = os.path.join(os.path.dirname(__file__), 'signature-fixtures.json')


def _load_test_cases() -> list:
    with open(_FIXTURES_FILE_PATH, encoding='UTF-8') as file:
        return from_json(file.read())


def _fix_base64_padding(data: str) -> str:
    return data + '=='


def _decode_b64(data: str) -> bytes:
    return base64.b64decode(_fix_base64_padding(data))


@pytest.mark.parametrize('test_case', _load_test_cases(), ids=lambda x: x['comment'])
def test_verify_signature(test_case: dict) -> None:
    did_key = test_case['publicKeyDid']
    data = _decode_b64(test_case['messageBase64'])
    signature = _decode_b64(test_case['signatureBase64'])
    expected_valid = test_case['validSignature']

    assert verify_signature(did_key, data, signature) == expected_valid

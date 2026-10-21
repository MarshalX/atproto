import json
import typing as t

import pytest
from atproto_client import models
from atproto_client.exceptions import ModelError
from atproto_client.models import get_model_as_dict, get_model_as_json, get_or_create

LABEL = {
    'src': 'did:plc:aaaaaaaaaaaaaaaaaaaaaaaa',
    'uri': 'at://did:plc:aaaaaaaaaaaaaaaaaaaaaaaa/app.bsky.feed.post/3k',
    'val': 'spam',
    'cts': '2026-01-01T00:00:00.000Z',
}
SIG = b'\x01\x02\xffsig'
#: unpadded base64 of SIG, as atproto JSON carries it
SIG_JSON = {'$bytes': 'AQL/c2ln'}


def test_json_bytes_object_is_decoded() -> None:
    response = get_or_create({'labels': [{**LABEL, 'sig': SIG_JSON}]}, models.ComAtprotoLabelQueryLabels.Response)

    assert response.labels[0].sig == SIG


def test_padded_base64_is_accepted() -> None:
    label = get_or_create({**LABEL, 'sig': {'$bytes': 'AQL/c2ln'}}, models.ComAtprotoLabelDefs.Label)
    padded = get_or_create({**LABEL, 'sig': {'$bytes': 'AQI='}}, models.ComAtprotoLabelDefs.Label)

    assert label.sig == SIG
    assert padded.sig == b'\x01\x02'


def test_cbor_bytes_pass_through() -> None:
    assert get_or_create({**LABEL, 'sig': SIG}, models.ComAtprotoLabelDefs.Label).sig == SIG


@pytest.mark.parametrize('sig', ['AQL/c2ln', {'$bytes': 'not base64!'}, {'$bytes': 1}, {'$bytes': 'AQI=', 'x': 1}])
def test_anything_else_is_rejected(sig: object) -> None:
    with pytest.raises(ModelError):
        get_or_create({**LABEL, 'sig': sig}, models.ComAtprotoLabelDefs.Label)


def test_json_dump_uses_the_atproto_form_and_round_trips() -> None:
    label = get_or_create({**LABEL, 'sig': SIG}, models.ComAtprotoLabelDefs.Label)
    dumped: t.Dict[str, object] = json.loads(get_model_as_json(label))

    assert dumped['sig'] == SIG_JSON
    assert get_or_create(dumped, models.ComAtprotoLabelDefs.Label).sig == SIG


def test_python_dump_keeps_raw_bytes() -> None:
    label = get_or_create({**LABEL, 'sig': SIG_JSON}, models.ComAtprotoLabelDefs.Label)

    assert get_model_as_dict(label)['sig'] == SIG


def test_record_with_bytes_is_typed() -> None:
    record = get_or_create(
        {'$type': 'com.germnetwork.declaration', 'version': '1.0.0', 'currentKey': {'$bytes': 'AQI'}},
        models.ComGermnetworkDeclaration.Record,
    )

    assert record.current_key == b'\x01\x02'

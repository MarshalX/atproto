import base64
import json

from atproto_client import models
from atproto_client.models import get_model_as_dict, get_model_as_json, get_or_create
from atproto_client.models.blob_ref import BlobRef, IpldLink
from atproto_core.cid import CID


def test_blob_ref_from_ipld() -> None:
    plain_cid = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'
    plain_blob_ref = {
        'mimeType': 'text/plain',
        'size': 0,
        '$type': 'blob',
        'ref': plain_cid,
    }
    instance = get_or_create(plain_blob_ref, BlobRef)

    assert isinstance(instance, BlobRef)
    assert instance.cid == CID.decode(plain_cid)


def test_blob_ref_from_ipld_json() -> None:
    plain_cid = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'

    plain_blob_ref = {
        'mimeType': 'text/plain',
        'size': 0,
        '$type': 'blob',
        'ref': {'$link': plain_cid},
    }
    instance = get_or_create(plain_blob_ref, BlobRef)

    assert isinstance(instance, BlobRef)
    assert instance.cid == CID.decode(plain_cid)
    assert isinstance(instance.ref, IpldLink)
    assert not isinstance(instance.ref, str)

    plain_blob_ref2 = get_model_as_dict(instance)
    assert plain_blob_ref2 == plain_blob_ref

    instance2 = get_or_create(plain_blob_ref2, BlobRef)
    assert instance2.cid == CID.decode(plain_cid)
    assert isinstance(instance2.ref, IpldLink)
    assert not isinstance(instance2.ref, str)

    assert instance2 == instance
    assert instance2.cid == instance.cid
    assert instance2.ref.link == instance.ref.link


def test_blob_ref_to_ipld() -> None:
    plain_cid = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'
    blob_ref = BlobRef(
        mime_type='text/plain',
        size=0,
        ref=plain_cid,
    )
    assert plain_cid == blob_ref.ref
    assert not isinstance(blob_ref.ref, IpldLink)
    assert isinstance(blob_ref.ref, str)

    # round trip
    blob_ref2 = get_or_create(get_model_as_dict(blob_ref), BlobRef)
    assert plain_cid == blob_ref2.ref
    assert not isinstance(blob_ref2.ref, IpldLink)
    assert isinstance(blob_ref2.ref, str)

    assert blob_ref2 == blob_ref
    assert blob_ref2.ref == blob_ref.ref

    # verify RAW ref representation
    blob_ref2_raw = get_model_as_dict(blob_ref)
    assert isinstance(blob_ref2_raw['ref'], str)
    assert plain_cid == blob_ref2_raw['ref']


def test_blob_ref_to_ipld_json() -> None:
    plain_cid = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'

    blob_ref = BlobRef(
        mime_type='text/plain',
        size=0,
        ref=IpldLink(link=plain_cid),
    )
    assert plain_cid == blob_ref.ref.link
    assert isinstance(blob_ref.ref, IpldLink)
    assert not isinstance(blob_ref.ref, str)

    # round trip
    blob_ref2 = get_or_create(get_model_as_dict(blob_ref), BlobRef)
    assert plain_cid == blob_ref2.ref.link
    assert isinstance(blob_ref2.ref, IpldLink)
    assert not isinstance(blob_ref2.ref, str)

    assert blob_ref2 == blob_ref
    assert blob_ref2.ref == blob_ref.ref
    assert blob_ref2.ref.link == blob_ref.ref.link

    # verify JSON ref representation
    blob_ref2_raw = get_model_as_dict(blob_ref)
    assert '$link' in blob_ref2_raw['ref']
    assert plain_cid == blob_ref2_raw['ref']['$link']


def test_blob_ref_to_json_representation() -> None:
    plain_cid = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'

    bytes_blob_ref = BlobRef(
        mime_type='text/plain',
        size=0,
        ref=plain_cid,
    )

    json_blob_ref = bytes_blob_ref.to_json_representation()
    assert not json_blob_ref.is_bytes_representation
    assert json_blob_ref.is_json_representation
    assert json_blob_ref.ref.link == bytes_blob_ref.ref
    assert json_blob_ref.ref.link == plain_cid

    json_blob_ref2 = BlobRef(
        mime_type='text/plain',
        size=0,
        ref=IpldLink(link=plain_cid),
    )
    # JSON to JSON representation (nothing should happen)
    json_blob_ref3 = json_blob_ref2.to_json_representation()
    assert json_blob_ref3 is not json_blob_ref2
    assert json_blob_ref3 == json_blob_ref2
    assert json_blob_ref3.ref.link == bytes_blob_ref.ref


def test_blob_ref_to_bytes_representation() -> None:
    plain_cid = 'bafyreidfayvfuwqa7qlnopdjiqrxzs6blmoeu4rujcjtnci5beludirz2a'

    json_blob_ref = BlobRef(
        mime_type='text/plain',
        size=0,
        ref=IpldLink(link=plain_cid),
    )

    bytes_blob_ref = json_blob_ref.to_bytes_representation()
    assert bytes_blob_ref.is_bytes_representation
    assert not bytes_blob_ref.is_json_representation
    assert bytes_blob_ref.ref == json_blob_ref.ref.link
    assert bytes_blob_ref.ref == plain_cid

    bytes_blob_ref2 = BlobRef(
        mime_type='text/plain',
        size=0,
        ref=plain_cid,
    )
    # Bytes to Bytes representation (nothing should happen)
    bytes_blob_ref3 = bytes_blob_ref2.to_bytes_representation()
    assert bytes_blob_ref3 is not bytes_blob_ref2
    assert bytes_blob_ref3 == bytes_blob_ref2
    assert bytes_blob_ref3.ref == json_blob_ref.ref.link


_RAW_CID_STR = 'bafkreicwqcugdgubtawr6xv6jjifoju67eigwx2xgz4zs73nkzzn36oucy'
_RAW_CID_BYTES = base64.b64decode('AVUSIFaAqGGagZgtH16+SlBXJp75EGtfVzZ5mX9tVnLd+dQW')


def test_blob_ref_from_raw_cid_bytes_dumps_to_json() -> None:
    """A CBOR-decoded blob used to raise PydanticSerializationError here."""
    blob = BlobRef(mime_type='image/jpeg', size=1234, ref=_RAW_CID_BYTES)

    dumped = json.loads(blob.model_dump_json())

    assert dumped['ref'] == {'$link': _RAW_CID_STR}


def test_blob_ref_from_raw_cid_bytes_keeps_bytes_in_dict_dump() -> None:
    """The dict path feeds Firehose and CAR consumers; it must stay lossless."""
    blob = BlobRef(mime_type='image/jpeg', size=1234, ref=_RAW_CID_BYTES)

    assert get_model_as_dict(blob)['ref'] == _RAW_CID_BYTES


def test_blob_ref_from_raw_cid_bytes_round_trips_through_json() -> None:
    blob = BlobRef(mime_type='image/jpeg', size=1234, ref=_RAW_CID_BYTES)

    reloaded = get_or_create(json.loads(blob.model_dump_json()), BlobRef)

    assert isinstance(reloaded.ref, IpldLink)
    assert reloaded.cid == blob.cid


def test_blob_ref_from_raw_cid_bytes_to_json_representation() -> None:
    """to_json_representation used to raise ValidationError on the one case it documents."""
    blob = BlobRef(mime_type='image/jpeg', size=1234, ref=_RAW_CID_BYTES)

    converted = blob.to_json_representation()

    assert converted.is_json_representation
    assert converted.ref.link == _RAW_CID_STR
    assert converted.cid == blob.cid


def test_blob_ref_outgoing_json_is_a_valid_atproto_blob() -> None:
    """get_model_as_json is what the XRPC request path sends."""
    blob = BlobRef(mime_type='image/jpeg', size=1234, ref=_RAW_CID_BYTES)

    sent = json.loads(get_model_as_json(blob))

    assert sent == {'$type': 'blob', 'mimeType': 'image/jpeg', 'size': 1234, 'ref': {'$link': _RAW_CID_STR}}


def test_record_with_a_cbor_blob_dumps_to_json() -> None:
    """The reported case: embed.images[].image carrying a CBOR blob."""
    record = models.get_or_create(
        {
            '$type': 'app.bsky.feed.post',
            'text': 'look at this',
            'createdAt': '2026-08-18T00:00:00.000Z',
            'embed': {
                '$type': 'app.bsky.embed.images',
                'images': [
                    {
                        'alt': 'a cat',
                        'image': {'$type': 'blob', 'mimeType': 'image/jpeg', 'size': 1, 'ref': _RAW_CID_BYTES},
                    }
                ],
            },
        },
        models.AppBskyFeedPost.Record,
        strict=False,
    )

    dumped = json.loads(record.model_dump_json())

    assert dumped['embed']['images'][0]['image']['ref'] == {'$link': _RAW_CID_STR}

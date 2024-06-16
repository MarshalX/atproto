from atproto_client.models import get_model_as_dict, get_or_create
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

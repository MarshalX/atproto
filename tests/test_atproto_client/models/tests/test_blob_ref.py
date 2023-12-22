from atproto_client.models import get_or_create
from atproto_client.models.blob_ref import BlobRef
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

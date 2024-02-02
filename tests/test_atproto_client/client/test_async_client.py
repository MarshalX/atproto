import warnings

import pytest
from atproto_client import AsyncClient, models


def test_strong_ref_arg_backward_compatibility() -> None:
    uri = 'at://...'
    cid = 'abc...'

    with warnings.catch_warnings(record=True) as w:
        # old flow
        ref = AsyncClient._strong_ref_arg_backward_compatibility(models.ComAtprotoRepoStrongRef.Main(cid=cid, uri=uri))
        assert ref.cid == cid and ref.uri == uri

        # old flow by name
        ref = AsyncClient._strong_ref_arg_backward_compatibility(
            subject=models.ComAtprotoRepoStrongRef.Main(cid=cid, uri=uri)
        )
        assert ref.cid == cid and ref.uri == uri

        assert len(w) == 2

    # new flow
    ref = AsyncClient._strong_ref_arg_backward_compatibility(uri, cid)
    assert ref.cid == cid and ref.uri == uri

    # new flow without required CID
    with pytest.raises(ValueError):
        AsyncClient._strong_ref_arg_backward_compatibility(uri)

    # new flow without required URI
    with pytest.raises(ValueError):
        AsyncClient._strong_ref_arg_backward_compatibility(cid=cid)

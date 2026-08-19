import pytest
from atproto_client import models
from pydantic import ValidationError

_CREATED_AT = '2024-02-22T19:58:13.903293+00:00'
_POST_URI = 'at://did:plc:aaaaaaaaaaaaaaaaaaaaaaaa/app.bsky.feed.post/3kkkkkkkkkk2a'


def test_array_item_constraint_is_applied() -> None:
    with pytest.raises(ValidationError):
        models.AppBskyFeedPost.Record(text='text', created_at=_CREATED_AT, tags=['t' * 641])

    record = models.AppBskyFeedPost.Record(text='text', created_at=_CREATED_AT, tags=['t' * 640])
    assert record.tags == ['t' * 640]


def test_array_constraint_is_applied() -> None:
    with pytest.raises(ValidationError):
        models.AppBskyFeedPost.Record(text='text', created_at=_CREATED_AT, tags=['tag'] * 9)


def test_array_item_constraint_is_applied_to_integers() -> None:
    def build_response(received_parts: list) -> models.AppBskyVideoGetUploadStatus.Response:
        return models.AppBskyVideoGetUploadStatus.Response(
            job_id='job',
            part_count=2,
            part_size_bytes=1024,
            received_parts=received_parts,
            state='created',
            expires_at=_CREATED_AT,
        )

    with pytest.raises(ValidationError):
        build_response([0])

    assert build_response([1, 2]).received_parts == [1, 2]


def test_optional_array_with_constraint_is_not_required() -> None:
    assert models.AppBskyFeedThreadgate.Record.model_fields['allow'].is_required() is False

    record = models.AppBskyFeedThreadgate.Record(created_at=_CREATED_AT, post=_POST_URI)
    assert record.allow is None

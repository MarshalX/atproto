from atproto_client import models
from atproto_client.models import get_model_as_dict, get_or_create

from tests.test_atproto_client.models.tests.utils import load_data_from_file


def load_test_data() -> dict:
    return load_data_from_file('thread_view_post_with_embed_media')


def test_thread_view_post_with_embed_media_deserialization() -> None:
    model = get_or_create(load_test_data(), models.AppBskyFeedGetPostThread.Response)

    assert isinstance(model, models.AppBskyFeedGetPostThread.Response)
    assert isinstance(model.thread, models.AppBskyFeedDefs.ThreadViewPost)

    # FIXME (MarshalX): value of models.ids. They doesn't contain #
    assert model.thread.py_type == 'app.bsky.feed.defs#threadViewPost'
    assert model.thread.post.py_type == 'app.bsky.feed.defs#postView'
    assert model.thread.post.embed.py_type == 'app.bsky.embed.recordWithMedia#view'

    assert isinstance(model.thread.post.embed, models.AppBskyEmbedRecordWithMedia.View)
    assert isinstance(model.thread.post.embed.media, models.AppBskyEmbedImages.View)
    assert isinstance(model.thread.post.embed.media.images, list)
    assert len(model.thread.post.embed.media.images) == 1


def test_thread_view_post_with_embed_media_serialization() -> None:
    model = get_or_create(load_test_data(), models.AppBskyFeedGetPostThread.Response)
    model_dict = get_model_as_dict(model)

    restored_model = get_or_create(model_dict, models.AppBskyFeedGetPostThread.Response)
    assert model_dict == get_model_as_dict(restored_model)
    assert isinstance(restored_model.thread.post.embed, models.AppBskyEmbedRecordWithMedia.View)
    assert len(restored_model.thread.post.embed.media.images) == 1

import atproto
import atproto.models
import atproto_client.models
from atproto.models import AppBskyFeedPost, ids


def test_models_is_importable_as_a_submodule() -> None:
    assert AppBskyFeedPost.Record.model_fields
    assert ids.AppBskyFeedPost == 'app.bsky.feed.post'


def test_models_submodule_is_the_models_package() -> None:
    from atproto import models

    assert atproto.models is atproto_client.models
    assert models is atproto_client.models


def test_missing_dunder_raises_attribute_error() -> None:
    for name in ('__qualname__', '__wrapped__', '__does_not_exist__'):
        assert not hasattr(atproto_client.models, name)

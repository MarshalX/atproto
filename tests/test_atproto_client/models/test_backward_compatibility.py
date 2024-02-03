import warnings

from atproto_client import models


def test_record_model_name_backward_compatibility() -> None:
    with warnings.catch_warnings(record=True) as w:
        models.AppBskyFeedPost.Main(text='text', created_at='time')

        assert len(w) == 1
        assert issubclass(w[0].category, DeprecationWarning)

    with warnings.catch_warnings(record=True) as w:
        class MyModel(models.AppBskyFeedPost.Main):
            pass

        MyModel(text='text', created_at='time')

        assert len(w) == 2
        assert issubclass(w[0].category, DeprecationWarning)
        assert issubclass(w[1].category, DeprecationWarning)

    with warnings.catch_warnings(record=True) as w:
        models.AppBskyFeedPost.Record(text='text', created_at='time')

        assert len(w) == 0

    with warnings.catch_warnings(record=True) as w:
        class MyModel(models.AppBskyFeedPost.Record):
            pass

        MyModel(text='text', created_at='time')

        assert len(w) == 0

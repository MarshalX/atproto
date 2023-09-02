import typing as t

from atproto.xrpc_client import models
from atproto.xrpc_client.models import get_model_as_dict, get_or_create
from tests.models.tests.utils import load_data_from_file

TEST_DATA = load_data_from_file('get_follows')


def _find_muted_follow(
    model: models.AppBskyGraphGetFollows.Response,
) -> t.Optional[models.AppBskyActorDefs.ProfileView]:
    for follow in model.follows:
        if follow.viewer.muted_by_list:
            return follow

    return None


def test_get_follows_deserialization():
    """Test deserialization of literals and tokens from get_follows response.

    Note:
        The response must contain at least one mutedByList follow.
    """
    model = get_or_create(TEST_DATA, models.AppBskyGraphGetFollows.Response)

    assert isinstance(model, models.AppBskyGraphGetFollows.Response)

    expected_purpose = 'app.bsky.graph.defs#modlist'

    muted_by_list_follow = _find_muted_follow(model)
    assert muted_by_list_follow is not None
    assert isinstance(muted_by_list_follow, models.AppBskyActorDefs.ProfileView)
    assert muted_by_list_follow.viewer.muted_by_list.purpose == expected_purpose
    assert muted_by_list_follow.viewer.muted is True


def test_get_follows_serialization():
    """Test serialization of literals and tokens from get_follows response.

    Note:
        The response must contain at least one mutedByList follow.
    """
    model = get_or_create(TEST_DATA, models.AppBskyGraphGetFollows.Response)

    model_dict = get_model_as_dict(model)
    restored_model = get_or_create(model_dict, models.AppBskyGraphGetFollows.Response)

    assert isinstance(get_model_as_dict(model), dict)
    assert model_dict == get_model_as_dict(restored_model)

    expected_purpose = 'app.bsky.graph.defs#modlist'

    restored_muted_by_list_follow = _find_muted_follow(restored_model)
    assert restored_muted_by_list_follow is not None
    assert isinstance(restored_muted_by_list_follow, models.AppBskyActorDefs.ProfileView)
    assert restored_muted_by_list_follow.viewer.muted_by_list.purpose == expected_purpose
    assert restored_muted_by_list_follow.viewer.muted is True

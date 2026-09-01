import typing as t
from pathlib import Path

import libipld
import pytest
from atproto_codegen.config import CodegenConfig
from atproto_codegen.models.generator import generate_models
from atproto_codegen.subscriptions.generator import generate_subscriptions
from atproto_subscription.frames import Frame

from .conftest import CUSTOM_LEXICON_DIR

PACKAGE = 'subs_pkg'


def _frame(fragment: str, body: dict) -> t.Any:
    return Frame.from_bytes(libipld.encode_dag_cbor({'op': 1, 't': fragment}) + libipld.encode_dag_cbor(body))


@pytest.fixture(scope='module')
def subscriptions(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[t.Any]:
    import importlib
    import sys

    root = tmp_path_factory.mktemp('subs')
    config = CodegenConfig(
        emit_lexicon_dirs=(CUSTOM_LEXICON_DIR,),
        output_dir=root.joinpath(PACKAGE),
        package=PACKAGE,
    )
    generate_models(config)
    generate_subscriptions(config)

    sys.path.insert(0, str(root))
    yield importlib.import_module(f'{PACKAGE}.subscriptions')


def test_message_union_and_map_are_generated(subscriptions: t.Any) -> None:
    assert subscriptions.XyzStatusphereSubscribeStatusesMessage is not None
    assert sorted(subscriptions.XYZ_STATUSPHERE_SUBSCRIBE_STATUSES_MESSAGE_TYPE_TO_MODEL) == ['#info', '#update']


def test_sync_and_async_clients_are_generated(subscriptions: t.Any) -> None:
    assert subscriptions.XyzStatusphereSubscribeStatusesClient is not None
    assert subscriptions.AsyncXyzStatusphereSubscribeStatusesClient is not None


def test_parse_decodes_a_real_frame(subscriptions: t.Any) -> None:
    message = subscriptions.parse_xyz_statusphere_subscribe_statuses_message(
        _frame('#update', {'seq': 42, 'status': '🚀', 'did': 'did:plc:aaaaaaaaaaaaaaaaaaaaaaaa'})
    )

    assert type(message).__module__.startswith(PACKAGE)
    assert message.seq == 42
    assert message.status == '🚀'


def test_client_builds_the_subscription_uri(subscriptions: t.Any) -> None:
    client = subscriptions.XyzStatusphereSubscribeStatusesClient(
        base_uri='wss://example.invalid/xrpc', params={'cursor': 42}
    )

    assert client._websocket_uri == 'wss://example.invalid/xrpc/xyz.statusphere.subscribeStatuses?cursor=42'


def test_subprotocol_subscriptions_get_no_client() -> None:
    """Jetstream declares a subprotocol, so the standard framing client does not apply to it."""
    from atproto_client import subscriptions

    assert hasattr(subscriptions, 'NETWORK_BSKY_JETSTREAM_SUBSCRIBE_EVENTS_MESSAGE_TYPE_TO_MODEL')
    assert not hasattr(subscriptions, 'NetworkBskyJetstreamSubscribeEventsClient')


def test_firehose_public_api_is_unchanged() -> None:
    import atproto
    from atproto_client import subscriptions

    assert atproto.FirehoseSubscribeReposClient.__mro__[1] is subscriptions.ComAtprotoSyncSubscribeReposClient
    assert atproto.parse_subscribe_repos_message is subscriptions.parse_com_atproto_sync_subscribe_repos_message
    assert atproto.firehose_models.MessageFrame.__module__ == 'atproto_subscription.frames'


def test_generated_subscriptions_file_exists(subscriptions: t.Any) -> None:
    assert Path(subscriptions.__file__).name == 'subscriptions.py'

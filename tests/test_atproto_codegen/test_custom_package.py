import sys
import typing as t
from pathlib import Path

import pytest
from atproto_cli import atproto_cli
from atproto_client.request import Response
from click.testing import CliRunner

CUSTOM_LEXICON_DIR = Path(__file__).parent.parent.joinpath('fixtures', 'custom_lexicons').absolute()
PACKAGE = 'statusphere'

_STATUSES_PAYLOAD = {
    'statuses': [{'uri': 'at://did:plc:test/xyz.statusphere.status/abc', 'status': '🎉'}],
    'cursor': 'next',
}


def _generate(root: Path, *extra: str) -> None:
    result = CliRunner().invoke(
        atproto_cli,
        [
            'gen',
            '--lexicon-dir',
            str(CUSTOM_LEXICON_DIR),
            'custom',
            '--output-dir',
            str(root.joinpath(PACKAGE)),
            '--package',
            PACKAGE,
            *extra,
        ],
    )

    assert result.exit_code == 0, result.output


@pytest.fixture(scope='module')
def package(tmp_path_factory: pytest.TempPathFactory) -> t.Iterator[t.Any]:
    import importlib

    root = tmp_path_factory.mktemp('cli')
    _generate(root)

    sys.path.insert(0, str(root))
    try:
        yield importlib.import_module(PACKAGE)
    finally:
        sys.path.remove(str(root))
        for name in [n for n in sys.modules if n.startswith(PACKAGE)]:
            del sys.modules[name]


@pytest.fixture
def calls() -> t.List[t.Tuple[str, t.Any]]:
    return []


@pytest.fixture
def client(package: t.Any, calls: t.List[t.Tuple[str, t.Any]], monkeypatch: pytest.MonkeyPatch) -> t.Any:
    import importlib

    from atproto_client.client.base import ClientBase

    def fake_invoke_query(self: t.Any, nsid: str, **kwargs: t.Any) -> Response:
        calls.append((nsid, kwargs.get('params')))
        return Response(success=True, status_code=200, content=_STATUSES_PAYLOAD, headers={})

    monkeypatch.setattr(ClientBase, 'invoke_query', fake_invoke_query)

    client_module = importlib.import_module(f'{PACKAGE}.client')
    return client_module.StatusphereClient()


def test_cli_emits_a_complete_package(package: t.Any) -> None:
    root = Path(package.__file__).parent

    for expected in ('__init__.py', 'client.py', 'async_client.py'):
        assert root.joinpath(expected).is_file(), expected
    assert root.joinpath('models', 'xyz', 'statusphere', 'status.py').is_file()
    assert root.joinpath('namespaces', 'sync_ns.py').is_file()


def test_client_exposes_the_custom_namespace(client: t.Any) -> None:
    assert hasattr(client, 'xyz')
    assert hasattr(client.xyz, 'statusphere')


def test_client_keeps_the_sdk_namespaces(client: t.Any) -> None:
    """The generated client subclasses the SDK's, so app.bsky is still reachable."""
    assert hasattr(client, 'app')
    assert hasattr(client, 'com')


def test_calling_a_custom_method_hits_the_right_nsid(client: t.Any, calls: t.List[t.Tuple[str, t.Any]]) -> None:
    response = client.xyz.statusphere.get_statuses({'limit': 10})

    assert [nsid for nsid, _ in calls] == ['xyz.statusphere.getStatuses']
    assert calls[0][1].limit == 10
    assert response.cursor == 'next'
    assert response.statuses[0].status == '🎉'


def test_response_is_typed_by_the_generated_model(client: t.Any, package: t.Any) -> None:
    import importlib

    models = importlib.import_module(f'{PACKAGE}.models')
    response = client.xyz.statusphere.get_statuses()

    assert isinstance(response, models.XyzStatusphereGetStatuses.Response)
    assert type(response.statuses[0]).__module__.startswith(PACKAGE)


def test_attach_adds_namespaces_to_an_existing_client(package: t.Any, monkeypatch: pytest.MonkeyPatch) -> None:
    import importlib

    from atproto_client import Client

    plain = Client()
    assert not hasattr(plain, 'xyz')

    importlib.import_module(f'{PACKAGE}.client').attach_namespaces(plain)

    assert hasattr(plain, 'xyz')


def test_no_client_flag_skips_client_generation(tmp_path: Path) -> None:
    _generate(tmp_path, '--no-client')
    root = tmp_path.joinpath(PACKAGE)

    assert root.joinpath('models').is_dir()
    assert not root.joinpath('client.py').exists()
    assert not root.joinpath('async_client.py').exists()

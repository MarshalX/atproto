import subprocess
import sys
import typing as t

import atproto
import pytest


def _imported_modules(statement: str) -> t.Set[str]:
    code = f'import sys\n{statement}\nprint("\\n".join(sys.modules))'
    output = subprocess.run(  # noqa: S603
        [sys.executable, '-c', code], capture_output=True, text=True, check=True
    ).stdout

    return set(output.split())


def test_every_public_name_resolves() -> None:
    for name in atproto.__all__:
        assert getattr(atproto, name) is not None
        assert name in dir(atproto)


def test_unknown_name_raises_attribute_error() -> None:
    with pytest.raises(AttributeError):
        _ = atproto.DoesNotExist


def test_importing_the_package_loads_nothing_else() -> None:
    modules = _imported_modules('import atproto')

    assert {module for module in modules if module.startswith('atproto_')} == {
        'atproto_core',
        'atproto_core.lazy_exports',
    }


def test_client_does_not_load_streams_or_crypto() -> None:
    modules = _imported_modules('from atproto import Client')

    assert 'atproto_firehose' not in modules
    assert 'atproto_jetstream' not in modules
    assert 'cryptography' not in modules


def test_firehose_does_not_load_the_http_client() -> None:
    modules = _imported_modules('from atproto import FirehoseSubscribeReposClient')

    assert 'httpx' not in modules
    assert 'atproto_client.client.client' not in modules


def test_client_package_exposes_its_submodules() -> None:
    code = 'import atproto_client\nprint(atproto_client.exceptions.__name__, atproto_client.request.__name__)'
    output = subprocess.run(  # noqa: S603
        [sys.executable, '-c', code], capture_output=True, text=True, check=True
    ).stdout

    assert output.split() == ['atproto_client.exceptions', 'atproto_client.request']


def test_client_package_raises_attribute_error_for_unknown_names() -> None:
    import atproto_client

    with pytest.raises(AttributeError):
        _ = atproto_client.does_not_exist


def _always_valid(*_: object) -> bool:
    return True


def _patched_did_key(*_: object) -> str:
    return 'did:key:patched'


def test_crypto_aliases_stay_patchable(monkeypatch: pytest.MonkeyPatch) -> None:
    from atproto_core.did_doc import did_doc
    from atproto_server.auth import jwt

    monkeypatch.setattr(jwt, 'verify_signature', _always_valid)
    monkeypatch.setattr(did_doc, 'get_did_key', _patched_did_key)

    assert jwt._verify_signature('key', b'input', b'signature') is True
    assert did_doc.get_did_key('Multikey', 'z') == 'did:key:patched'

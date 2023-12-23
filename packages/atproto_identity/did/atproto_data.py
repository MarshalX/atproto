import typing as t

from atproto_identity.did.models import AtprotoData

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument


def ensure_atproto_document(_: 'DidDocument') -> AtprotoData:
    raise NotImplementedError


def ensure_atproto_key(_: 'DidDocument') -> str:
    raise NotImplementedError

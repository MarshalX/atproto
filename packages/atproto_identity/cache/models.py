import typing as t
from dataclasses import dataclass
from datetime import datetime

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument


@dataclass
class CachedDid:
    document: 'DidDocument'
    updated_at: datetime


@dataclass
class CachedDidResult:
    did: str
    document: 'DidDocument'
    updated_at: datetime
    stale: bool
    expired: bool

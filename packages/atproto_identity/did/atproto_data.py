import typing as t
from dataclasses import dataclass

from atproto_identity.exceptions import AtprotoDataParseError

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument


@dataclass
class AtprotoData:
    did: str
    signing_key: t.Optional[str] = None
    handle: t.Optional[str] = None
    pds: t.Optional[str] = None

    @classmethod
    def from_did_doc(cls, did_doc: 'DidDocument') -> 'AtprotoData':
        return AtprotoData(
            did=did_doc.id,
            signing_key=did_doc.get_did_key(),
            handle=did_doc.get_handle(),
            pds=did_doc.get_pds_endpoint(),
        )


def ensure_atproto_document(did_doc: 'DidDocument') -> AtprotoData:
    atproto_data = AtprotoData.from_did_doc(did_doc)

    if atproto_data.did is None:
        raise AtprotoDataParseError(f'Could not parse did from doc: {did_doc}')
    if atproto_data.signing_key is None:
        raise AtprotoDataParseError(f'Could not parse signing_key from doc: {did_doc}')
    if atproto_data.handle is None:
        raise AtprotoDataParseError(f'Could not parse handle from doc: {did_doc}')
    if atproto_data.pds is None:
        raise AtprotoDataParseError(f'Could not parse pds from doc: {did_doc}')

    return atproto_data


def ensure_atproto_key(did_doc: 'DidDocument') -> str:
    atproto_data = AtprotoData.from_did_doc(did_doc)

    if atproto_data.signing_key is None:
        raise AtprotoDataParseError(f'Could not parse signing_key from doc: {did_doc}')

    return atproto_data.signing_key

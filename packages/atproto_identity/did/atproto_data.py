import typing as t
from dataclasses import dataclass

from atproto_crypto.consts import P256_JWT_ALG, SECP256K1_JWT_ALG
from atproto_crypto.did import format_did_key, parse_multikey
from atproto_crypto.multibase import multibase_to_bytes

if t.TYPE_CHECKING:
    from atproto_core.did_doc import DidDocument


@dataclass
class AtprotoData:
    did: str
    signing_key: str
    handle: str
    pds: str

    @classmethod
    def from_did_doc(cls, did_doc: 'DidDocument') -> 'AtprotoData':
        return parse_to_atproto_data(did_doc)


def get_did_key(did_doc: 'DidDocument') -> t.Optional[str]:
    key = did_doc.get_signing_key()
    if key is None:
        return None

    key_bytes = multibase_to_bytes(key.public_key_multibase)

    did_key = None
    if key.type == 'EcdsaSecp256r1VerificationKey2019':
        did_key = format_did_key(P256_JWT_ALG, key_bytes)
    elif key.type == 'EcdsaSecp256k1VerificationKey2019':
        did_key = format_did_key(SECP256K1_JWT_ALG, key_bytes)
    elif key.type == 'Multikey':
        parsed_key = parse_multikey(key.public_key_multibase)
        did_key = format_did_key(parsed_key.jwt_alg, parsed_key.key_bytes)

    return did_key


def parse_to_atproto_data(did_doc: 'DidDocument') -> AtprotoData:
    return AtprotoData(
        did=did_doc.id,
        signing_key=get_did_key(did_doc),
        handle=did_doc.get_handle(),
        pds=did_doc.get_pds_endpoint(),
    )


def ensure_atproto_document(did_doc: 'DidDocument') -> AtprotoData:
    atproto_data = AtprotoData.from_did_doc(did_doc)

    if atproto_data.did is None:
        raise ValueError(f'Could not parse did from doc: {did_doc}')
    if atproto_data.signing_key is None:
        raise ValueError(f'Could not parse signingKey from doc: {did_doc}')
    if atproto_data.handle is None:
        raise ValueError(f'Could not parse handle from doc: {did_doc}')
    if atproto_data.pds is None:
        raise ValueError(f'Could not parse pds from doc: {did_doc}')

    return atproto_data


def ensure_atproto_key(did_doc: 'DidDocument') -> str:
    atproto_data = AtprotoData.from_did_doc(did_doc)

    if atproto_data.signing_key is None:
        raise ValueError(f'Could not parse signingKey from doc: {did_doc}')

    return atproto_data.signing_key

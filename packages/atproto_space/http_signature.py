import typing as t

from atproto_crypto.algs.p256 import P256
from atproto_crypto.exceptions import UnsupportedKeyTypeError
from cryptography.hazmat.primitives.asymmetric import ec

from atproto_space._structured_fields import InnerList, Item, serialize_dictionary, serialize_inner_list, serialize_item

_P256: t.Final = P256()

SIGNATURE_INPUT_HEADER: t.Final = 'signature-input'
SIGNATURE_HEADER: t.Final = 'signature'

_AUTHORIZATION_HEADER: t.Final = 'authorization'
_AUTHORIZATION_SCHEME: t.Final = 'Atproto-Space-Credential'
_AUDIENCE_HEADER: t.Final = 'atproto-space-audience'

_SIGNATURE_PARAMS_COMPONENT: t.Final = '"@signature-params"'

_SIGNATURE_LABEL: t.Final = 'sig'
_SIGNATURE_TAG: t.Final = 'atproto-space-credential'


def build_signature_base(components: t.Sequence[str], values: t.Sequence[str], signature_params: str) -> bytes:
    """Build the signature base of an HTTP message signature (RFC 9421, section 2.5).

    Args:
        components: Serialized identifiers of the covered components, such as ``"authorization"``.
        values: Values of the covered components, in the same order.
        signature_params: Serialized signature parameters: the covered components followed by their parameters.

    Returns:
        :obj:`bytes`: Signature base.
    """
    lines = [f'{component}: {value.strip()}' for component, value in zip(components, values)]
    lines.append(f'{_SIGNATURE_PARAMS_COMPONENT}: {signature_params}')

    return '\n'.join(lines).encode('UTF-8')


def create_credential_headers(token: str, audience: str, private_key: ec.EllipticCurvePrivateKey) -> t.Dict[str, str]:
    """Create the headers that present a space credential to a host.

    The signature covers the credential and the audience only, so the headers suit every request to the audience.

    Args:
        token: Space credential.
        audience: DID of the repo for the methods of a repo, DID of the space authority for the methods of a space.
        private_key: P-256 private key that the credential is bound to.

    Returns:
        :obj:`dict`: Authorization, audience and signature headers.

    Raises:
        :class:`atproto_crypto.exceptions.UnsupportedKeyTypeError`: The private key is not a P-256 key.
    """
    if not isinstance(private_key.curve, ec.SECP256R1):
        raise UnsupportedKeyTypeError('Signature key must be a P-256 key')

    authorization = f'{_AUTHORIZATION_SCHEME} {token}'
    components = [Item(_AUTHORIZATION_HEADER), Item(_AUDIENCE_HEADER)]
    signature_input = InnerList(components, {'tag': _SIGNATURE_TAG})

    signature_base = build_signature_base(
        [serialize_item(component) for component in components],
        [authorization, audience],
        serialize_inner_list(signature_input),
    )
    signature = _P256.sign(private_key, signature_base)

    return {
        _AUTHORIZATION_HEADER: authorization,
        _AUDIENCE_HEADER: audience,
        SIGNATURE_INPUT_HEADER: serialize_dictionary({_SIGNATURE_LABEL: signature_input}),
        SIGNATURE_HEADER: serialize_dictionary({_SIGNATURE_LABEL: Item(signature)}),
    }

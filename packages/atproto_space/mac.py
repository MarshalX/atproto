import hashlib
import hmac
import typing as t

from atproto_space._structured_fields import (
    BareItem,
    InnerList,
    Item,
    Member,
    parse_dictionary,
    serialize_dictionary,
    serialize_inner_list,
    serialize_item,
)
from atproto_space.exceptions import SpaceMacError
from atproto_space.http_signature import SIGNATURE_HEADER, SIGNATURE_INPUT_HEADER, build_signature_base

if t.TYPE_CHECKING:
    from atproto_client import models
    from atproto_crypto.kem import Encapsulation

COMMIT_MAC_PROFILE: t.Final = 'atproto-space-commit'
RECORD_MAC_PROFILE: t.Final = 'atproto-space-record'

MAC_KEM_INFO: t.Final = b'atproto-mac'

_MAC_ALG: t.Final = 'hmac-sha256'
_MAC_LABEL: t.Final = 'mac'


def _get_components(profile: str) -> t.List[Item]:
    # a MAC covers the header named after its profile, as a structured field
    return [Item(profile, {'sf': True})]


def format_mac_request(profile: str, key_share: str) -> str:
    """Format the ``Accept-Signature`` header that asks a host for the MAC of its response.

    Args:
        profile: :obj:`COMMIT_MAC_PROFILE` or :obj:`RECORD_MAC_PROFILE`.
        key_share: Key share of the encapsulation that keys the MAC.

    Returns:
        :obj:`str`: Value of the header.
    """
    signature_params = InnerList(_get_components(profile), {'keyid': key_share, 'tag': profile})

    return serialize_dictionary({_MAC_LABEL: signature_params})


def _parse_header(headers: t.Mapping[str, str], name: str) -> t.Dict[str, Member]:
    value = headers.get(name)
    if value is None:
        raise SpaceMacError(f'Missing {name} header')

    try:
        return parse_dictionary(value)
    except ValueError as e:
        raise SpaceMacError(f'Malformed {name} header') from e


def _find_signature(headers: t.Mapping[str, str], profile: str, key_share: str) -> t.Tuple[InnerList, bytes]:
    signature_inputs = _parse_header(headers, SIGNATURE_INPUT_HEADER)
    signatures = _parse_header(headers, SIGNATURE_HEADER)

    # a label carries no meaning, so the tag is what identifies the signature
    tagged = [
        (label, member)
        for label, member in signature_inputs.items()
        if isinstance(member, InnerList) and member.params.get('tag') == profile
    ]
    if len(tagged) > 1:
        raise SpaceMacError(f'More than one signature with tag "{profile}"')

    if not tagged:
        raise SpaceMacError(f'Missing signature input with tag "{profile}"')

    label, signature_input = tagged[0]
    signature = signatures.get(label)
    if not isinstance(signature, Item) or not isinstance(signature.value, bytes) or signature.params:
        raise SpaceMacError(f'Missing or malformed signature with tag "{profile}"')

    components = serialize_inner_list(InnerList(_get_components(profile)))
    if serialize_inner_list(InnerList(signature_input.items)) != components:
        raise SpaceMacError(f'Signature must cover exactly {components}')

    params = signature_input.params
    if 'alg' in params and params['alg'] != _MAC_ALG:
        raise SpaceMacError(f'Signature algorithm must be {_MAC_ALG}')

    if 'keyid' in params and params['keyid'] != key_share:
        raise SpaceMacError('Signature keyid does not match the key share')

    return signature_input, signature.value


def _verify_mac(profile: str, encapsulation: 'Encapsulation', headers: t.Mapping[str, str]) -> t.Dict[str, Member]:
    signature_input, signature = _find_signature(headers, profile, encapsulation.key_share)
    fields = _parse_header(headers, profile)

    # the sf flag covers the header as serialized again from its parsed form
    signature_base = build_signature_base(
        [serialize_item(component) for component in _get_components(profile)],
        [serialize_dictionary(fields)],
        serialize_inner_list(signature_input),
    )
    mac = hmac.new(encapsulation.shared_secret, signature_base, hashlib.sha256).digest()
    if not hmac.compare_digest(mac, signature):
        raise SpaceMacError('MAC does not match')

    return fields


def _get_bare_item(fields: t.Mapping[str, Member], name: str) -> t.Optional[BareItem]:
    member = fields.get(name)
    return member.value if isinstance(member, Item) else None


def verify_commit_mac(
    commit: 'models.ComAtprotoSpaceDefs.Commit', encapsulation: 'Encapsulation', headers: t.Mapping[str, str]
) -> None:
    """Verify the MAC of a response and that the header it covers describes the commit.

    Args:
        commit: Commit from the response.
        encapsulation: Encapsulation whose key share the MAC was requested with.
        headers: Headers of the response, with names in lower case.

    Raises:
        :class:`atproto_space.exceptions.SpaceMacError`: The MAC is missing, malformed or wrong,
            or it covers another commit.
    """
    fields = _verify_mac(COMMIT_MAC_PROFILE, encapsulation, headers)

    ver = _get_bare_item(fields, 'ver')
    data = _get_bare_item(fields, 'data')
    matches = (
        # a boolean and a decimal are equal to the integer of the same value
        type(ver) is int
        and ver == commit.ver
        and _get_bare_item(fields, 'repo') == commit.repo
        and _get_bare_item(fields, 'space') == commit.space
        and _get_bare_item(fields, 'rev') == commit.rev
        and isinstance(data, bytes)
        and data == commit.data
    )
    if not matches:
        raise SpaceMacError('Commit does not match its MAC')


def verify_record_mac(uri: str, cid: str, encapsulation: 'Encapsulation', headers: t.Mapping[str, str]) -> None:
    """Verify the MAC of a response and that the header it covers names the record.

    Args:
        uri: URI of the record that was requested.
        cid: CID of the record from the response.
        encapsulation: Encapsulation whose key share the MAC was requested with.
        headers: Headers of the response, with names in lower case.

    Raises:
        :class:`atproto_space.exceptions.SpaceMacError`: The MAC is missing, malformed or wrong,
            or it covers another record.
    """
    fields = _verify_mac(RECORD_MAC_PROFILE, encapsulation, headers)

    if _get_bare_item(fields, 'uri') != uri or _get_bare_item(fields, 'cid') != cid:
        raise SpaceMacError('Record does not match its MAC')

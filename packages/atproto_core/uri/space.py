import re
import typing as t
from dataclasses import dataclass

from atproto_core.exceptions import InvalidAtUriError
from atproto_core.nsid import validate_nsid

_SPACE_MARKER: t.Final = 'space'

_MAX_URI_LEN: t.Final = 8192
_MAX_DID_LEN: t.Final = 2048

# ref: https://github.com/bluesky-social/atproto/blob/b5fd12fa57b10cf068efa879812f558780f37109/packages/syntax/src/aturi_validation.ts#L211-L212
_SPACE_URI_REGEX: t.Final = re.compile(
    r'at://(?P<space_did>[^/?#\s]+)/space/(?P<space_type>[^/?#\s]+)/(?P<skey>[^/?#\s]+)'
    r'(?:/(?P<author_did>[^/?#\s]+)/(?P<collection>[^/?#\s]+)/(?P<rkey>[^/?#\s]+))?'
    r'(?P<trailing_slash>/)?(?P<query>\?[^#\s]*)?(?P<fragment>#\S*)?'
)
_DID_REGEX: t.Final = re.compile(r'did:[a-z]+:[a-zA-Z0-9._:%-]*[a-zA-Z0-9._-]')
_RECORD_KEY_REGEX: t.Final = re.compile(r'[A-Za-z0-9._:~-]{1,512}')
_RECORD_KEY_FORBIDDEN: t.Final = frozenset({'.', '..'})


def is_did(value: str) -> bool:
    return len(value) <= _MAX_DID_LEN and _DID_REGEX.fullmatch(value) is not None


def _is_nsid(value: str) -> bool:
    return validate_nsid(value, soft_fail=True)


def is_record_key(value: str) -> bool:
    return _RECORD_KEY_REGEX.fullmatch(value) is not None and value not in _RECORD_KEY_FORBIDDEN


_SPACE_URI_PART_VALIDATORS: t.Final[t.Dict[str, t.Callable[[str], bool]]] = {
    'space_did': is_did,
    'space_type': _is_nsid,
    'skey': is_record_key,
    'author_did': is_did,
    'collection': _is_nsid,
    'rkey': is_record_key,
}


def _parse_space_uri(uri: str) -> t.Dict[str, str]:
    if len(uri) > _MAX_URI_LEN:
        raise InvalidAtUriError(f'Space URI is too long. Max len: {_MAX_URI_LEN}')

    match = _SPACE_URI_REGEX.fullmatch(uri)
    if not match:
        raise InvalidAtUriError('Space URI must be at://<did>/space/<type>/<skey>[/<did>/<collection>/<rkey>]')

    parts = match.groupdict('')
    if parts['trailing_slash'] or parts['query'] or parts['fragment']:
        raise InvalidAtUriError('Space URI cannot have a trailing slash, query or fragment')

    for name, is_valid in _SPACE_URI_PART_VALIDATORS.items():
        if parts[name] and not is_valid(parts[name]):
            raise InvalidAtUriError(f'Space URI has invalid {name}')

    return parts


@dataclass(frozen=True)
class SpaceRef:
    """Reference to a space.

    Example:
        at://did:plc:ewvi7nxzyoun6zhxrhs64oiz/space/app.bsky.group/default
    """

    space_did: str
    space_type: str
    skey: str

    @classmethod
    def from_str(cls, uri: str) -> 'SpaceRef':
        """Create `SpaceRef` instance from URI of the space."""
        parts = _parse_space_uri(uri)
        if parts['author_did']:
            raise InvalidAtUriError('Space reference cannot name a record')

        return cls(space_did=parts['space_did'], space_type=parts['space_type'], skey=parts['skey'])

    @classmethod
    def from_uri(cls, uri: str) -> 'SpaceRef':
        """Create `SpaceRef` instance from URI of the space or of a record in it."""
        parts = _parse_space_uri(uri)
        return cls(space_did=parts['space_did'], space_type=parts['space_type'], skey=parts['skey'])

    def record_uri(self, repo: str, collection: str, rkey: str) -> str:
        """Get URI of a record in the space.

        Args:
            repo: DID of the account that the record belongs to.
            collection: NSID of the record collection.
            rkey: Record key.

        Returns:
            :obj:`str`: URI of the record.

        Raises:
            :class:`atproto.exceptions.InvalidAtUriError`: Invalid AT URI exception.
        """
        uri = f'{self}/{repo}/{collection}/{rkey}'
        _parse_space_uri(uri)

        return uri

    def __str__(self) -> str:
        return f'at://{self.space_did}/{_SPACE_MARKER}/{self.space_type}/{self.skey}'

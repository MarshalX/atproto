import re
import typing as t
import urllib.parse as urlparse
from urllib.parse import urlencode

from atproto.exceptions import InvalidAtUriError

# ref: https://github.com/bluesky-social/atproto/blob/8c19ce991a766fd9cff5023160853ab1cb106f21/packages/uri/src/index.ts#LL5C38-L5C38
_ATP_URI_REGEX = r'^(at:\/\/)?((?:did:[a-z0-9:%-]+)|(?:[a-z][a-z0-9.:-]*))(\/[^?#\s]*)?(\?[^#\s]+)?(#[^\s]+)?$'


class AtUri:
    """ATP URI Scheme.

    Examples:
        Repository: at://alice.host.com

        Repository: at://did:plc:bv6ggog3tya2z3vxsub7hnal

        Collection: at://alice.host.com/io.example.song

        Record: at://alice.host.com/io.example.song/3yI5-c1z-cc2p-1a

        Record Field: at://alice.host.com/io.example.song/3yI5-c1z-cc2p-1a#/title
    """

    def __init__(self, host: str, pathname: str, hash_: str, search_params: t.List[t.Tuple[str, t.Any]]) -> None:
        self.host = host
        self.pathname = pathname
        self.hash = hash_
        self.search_params = search_params

    @property
    def protocol(self) -> str:
        """Get protocol."""
        return 'at://'

    @property
    def origin(self) -> str:
        """Get origin."""
        return f'at://{self.host}'

    @property
    def hostname(self) -> str:
        """Get hostname."""
        return self.host

    @property
    def collection(self) -> str:
        """Get collection name."""
        for part in self.pathname.split('/'):
            if part:
                return part

        return ''

    @property
    def rkey(self) -> str:
        """Get record key (rkey)."""
        parts = [p for p in self.pathname.split('/') if p]
        if len(parts) > 1:
            return parts[1]

        return ''

    @property
    def http(self) -> str:
        """Convert instance to HTTP URI."""
        return str(self)

    @classmethod
    def from_str(cls, uri: str) -> 'AtUri':
        """Create `AtUri` instance from URI."""
        groups = re.findall(_ATP_URI_REGEX, uri, re.IGNORECASE)
        if not groups:
            raise InvalidAtUriError

        group = groups[0]
        return cls(host=group[1], pathname=group[2], hash_=group[4], search_params=urlparse.parse_qsl(group[3]))

    def __str__(self) -> str:
        path = self.pathname or '/'
        if not path.startswith('/'):
            path = f'/{path}'

        query = urlencode(self.search_params)
        if query:
            query = f'?{query}'

        hash_ = self.hash
        if hash_ and not hash_.startswith('#'):
            hash_ = f'#{hash_}'

        return f'at://{self.host}{path}{query}{hash_}'

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other) -> bool:
        if isinstance(other, AtUri):
            return hash(self) == hash(other)

        return False

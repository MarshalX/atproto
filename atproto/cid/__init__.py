from typing import Union

from multiformats import CID as MCID

# TODO(MarshalX): Implement more methods


class CID:
    """CID (Content IDentifier).

    Hash for Merkle Search Tree (MST).
    """

    def __init__(self, cid: MCID):
        self._cid = cid

    def encode(self) -> str:
        """Encodes the CID."""
        return self._cid.encode()

    @classmethod
    def decode(cls, cid: Union[str, bytes]) -> 'CID':
        """Decodes a CID from str or bytes."""
        return cls(MCID.decode(cid))

    @property
    def version(self) -> int:
        """Get CID version."""
        return self._cid.version

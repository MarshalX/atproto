from typing import Union

from multiformats import CID as MCID


# TODO(MarshalX): Implement
class CID:
    def __init__(self, cid: MCID):
        self._cid = cid

    def encode(self) -> str:
        return self._cid.encode()

    @classmethod
    def decode(cls, cid: Union[str, bytes]) -> 'CID':
        return cls(MCID.decode(cid))

    @property
    def version(self) -> int:
        return self._cid.version

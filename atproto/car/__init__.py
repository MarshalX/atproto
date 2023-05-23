import typing as t
from io import BytesIO

from .. import cbor, leb128
from ..cid import CID

Blocks = t.Dict[CID, dict]


class CAR:
    """CAR file."""

    _CID_V1_BYTES_LEN = 36

    def __init__(self, root: str, blocks: Blocks):
        self._root = root
        self._blocks = blocks

    @property
    def root(self):
        """Get root."""
        return self._root

    @property
    def blocks(self) -> Blocks:
        """Get blocks."""
        return self._blocks

    @classmethod
    def from_bytes(cls, data: bytes) -> 'CAR':
        """Decode CAR file.

        Note:
            You could pass as `data` response of `client.com.atproto.sync.get_repo`, for example.
            And another responses of methods in the `sync` namespace.

        Example:
            >>> from atproto import CAR, Client
            >>> client = Client()
            >>> client.login('my-handle', 'my-password')
            >>> repo = client.com.atproto.sync.get_repo({'did': client.me.did})
            >>> car_file = CAR.from_bytes(repo)
            >>> print(car_file.root)
            >>> print(car_file.blocks)

        Args:
            data: Content of the CAR file.

        Returns:
            :obj:`atproto.CAR`: Parsed CAR file.
        """
        stream = BytesIO(data)

        header_len, _ = leb128.u.decode_reader(stream)
        header = cbor.decode_dag(stream.read(header_len))
        root = header.get('roots')[0]

        blocks = {}
        while stream.tell() != len(data):
            block_len, _ = leb128.u.decode_reader(stream)
            cid = CID.decode(stream.read(CAR._CID_V1_BYTES_LEN))
            block = cbor.decode_dag(stream.read(block_len - CAR._CID_V1_BYTES_LEN))

            blocks[cid] = block

        return cls(root=root, blocks=blocks)

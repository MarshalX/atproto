from io import BytesIO
from typing import Dict

import dag_cbor

from .. import leb128
from ..cid import CID

Nodes = Dict[CID, dict]


class CAR:
    """CAR file."""

    _CID_V1_BYTES_LEN = 36

    def __init__(self, root: str, nodes: Nodes):
        self._root = root
        self._nodes = nodes

    @property
    def root(self):
        """Get root."""
        return self._root

    @property
    def nodes(self) -> Nodes:
        """Get nodes."""
        return self._nodes

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
            >>> print(car_file.nodes)

        Args:
            data: content of the file.

        Returns:
            :obj:`atproto.CAR`: Parsed CAR file.
        """
        repo = BytesIO(data)

        header_len, _ = leb128.u.decode_reader(repo)
        header = dag_cbor.decode(repo.read(header_len))
        root = header.get('roots')[0]

        nodes = {}
        while repo.tell() != len(data):
            block_len, _ = leb128.u.decode_reader(repo)
            cid = CID.decode(repo.read(CAR._CID_V1_BYTES_LEN))
            block = dag_cbor.decode(repo.read(block_len - CAR._CID_V1_BYTES_LEN))

            nodes[cid] = block

        return cls(root=root, nodes=nodes)

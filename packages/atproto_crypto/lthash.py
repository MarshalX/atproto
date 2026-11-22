import hashlib
import typing as t

from blake3 import blake3

LTHASH_STATE_SIZE: t.Final = 2048

_LANE_HIGH_BITS: t.Final = int.from_bytes(b'\x00\x80' * (LTHASH_STATE_SIZE // 2), 'little')
_LANE_LOW_BITS: t.Final = int.from_bytes(b'\xff\x7f' * (LTHASH_STATE_SIZE // 2), 'little')


def _expand(element: str) -> int:
    return int.from_bytes(blake3(element.encode('utf-8')).digest(length=LTHASH_STATE_SIZE), 'little')


class LtHash:
    """Homomorphic hash of a set.

    Each element expands to 1024 lanes that are added into the state, so the state depends on the elements
    of the set and not on the order they were added in. An element added twice is in the set twice.

    Args:
        state: State to continue from. The empty set by default.
    """

    def __init__(self, state: t.Optional[bytes] = None) -> None:
        if state is None:
            state = bytes(LTHASH_STATE_SIZE)
        if len(state) != LTHASH_STATE_SIZE:
            raise ValueError(f'LtHash state must be {LTHASH_STATE_SIZE} bytes, got {len(state)}')

        self._lanes = int.from_bytes(state, 'little')

    def add(self, element: str) -> None:
        """Add the element to the set.

        Args:
            element: Element of the set.
        """
        lanes = _expand(element)
        low_bits = (self._lanes & _LANE_LOW_BITS) + (lanes & _LANE_LOW_BITS)
        self._lanes = low_bits ^ ((self._lanes ^ lanes) & _LANE_HIGH_BITS)

    def remove(self, element: str) -> None:
        """Remove the element from the set.

        Args:
            element: Element of the set.
        """
        lanes = _expand(element)
        low_bits = (self._lanes | _LANE_HIGH_BITS) - (lanes & _LANE_LOW_BITS)
        self._lanes = low_bits ^ ((self._lanes ^ lanes ^ _LANE_HIGH_BITS) & _LANE_HIGH_BITS)

    @property
    def state(self) -> bytes:
        """Get state as 1024 little-endian 16-bit lanes."""
        return self._lanes.to_bytes(LTHASH_STATE_SIZE, 'little')

    def digest(self) -> bytes:
        """Get SHA-256 digest of the state.

        Returns:
            :obj:`bytes`: Digest of 32 bytes.
        """
        return hashlib.sha256(self.state).digest()

    def __eq__(self, other: object) -> bool:
        if isinstance(other, LtHash):
            return self._lanes == other._lanes

        return False

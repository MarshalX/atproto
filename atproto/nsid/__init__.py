import re
import typing as t
from dataclasses import dataclass, field

from atproto.exceptions import InvalidNsidError

_NSID_DELIM = '.'
_NSID_NAMESPACE = '*'

_MAX_NSID_LEN = 253 + 1 + 128
_MAX_NSID_DOMAIN_PART = 63
_MAX_NSID_NAME_PART = 128
_MIN_NSID_PART = 1
_MIN_NSID_SEGMENTS_COUNT = 3

_NSID_VALID_CHARS_REGEX = r'^[a-zA-Z0-9.-]*$'
_NSID_PART_VALID_CHARS_REGEX = r'^[a-zA-Z]'

_NSID_PART_FORBIDDEN_END = '-'

Segments = t.List[str]


@dataclass
class NSID:
    """NameSpaced IDs (NSIDs).

    Examples:
        com.example.status

        io.social.getFeed

        net.users.bob.ping
    """

    segments: Segments = field(default_factory=list)

    @classmethod
    def from_str(cls, nsid: str) -> 'NSID':
        """Create `NSID` instance from string."""
        validate_nsid(nsid)
        return cls(segments=get_nsid_segments(nsid))

    @property
    def authority(self) -> str:
        """Get authority of NSID.

        com.example.thing
        ^^^^^^^^^^^--------> example.com

        delim joined self.segments[:-1][::-1]
        """
        segments_without_name = self.segments[:-1]
        segments_without_name.reverse()

        return _NSID_DELIM.join(segments_without_name)

    @property
    def name(self) -> str:
        """Get name."""
        return self.segments[-1]

    def __str__(self) -> str:
        return _NSID_DELIM.join(self.segments)

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(self, other) -> bool:
        if isinstance(other, NSID):
            return hash(self) == hash(other)

        return False


def get_nsid_segments(nsid: str) -> Segments:
    return nsid.split('.')


def _exclude_nsid_namespace_if_exists(segments: Segments) -> str:
    last_segment = segments[-1]

    if last_segment == _NSID_NAMESPACE:
        segments = segments[:-1]

    return _NSID_DELIM.join(segments)


def _validate_nsid_segment(segment: str, is_last_segment: bool) -> bool:
    """Validate NSID segment.

    Args:
        segment: Segment to validate.
        is_last_segment: The last segment indicator.

    Returns:
        :obj:`bool`: Validation result is always True.

    Raises:
        :class:`atproto.exceptions.InvalidNsidError`: Invalid NSID exception.
    """

    segment_len = len(segment)

    if segment_len < _MIN_NSID_PART:
        raise InvalidNsidError(f'NSID segment is too short. Min len: {_MIN_NSID_PART}')

    if is_last_segment:
        if segment_len > _MAX_NSID_NAME_PART:
            raise InvalidNsidError(f'NSID name segment is too long. Max len: {_MAX_NSID_NAME_PART}')
    else:
        if segment_len > _MAX_NSID_DOMAIN_PART:
            raise InvalidNsidError(f'NSID domain segment is too long. Max len: {_MAX_NSID_DOMAIN_PART}')

    if segment.endswith(_NSID_PART_FORBIDDEN_END):
        raise InvalidNsidError(f'NSID segment contains invalid end symbol: {_NSID_PART_FORBIDDEN_END}')

    if not re.search(_NSID_PART_VALID_CHARS_REGEX, segment):
        raise InvalidNsidError('NSID segment must starts with ASCII letter')

    return True


def _validate_nsid(nsid: str) -> bool:
    """Validate NSID.

    Args:
        nsid: NSID to validate.

    Returns:
        :obj:`bool`: Validation result is always True.

    Raises:
        :class:`atproto.exceptions.InvalidNsidError`: Invalid NSID exception.
    """

    segments = get_nsid_segments(nsid)
    clean_nsid = _exclude_nsid_namespace_if_exists(segments)
    clean_segments = get_nsid_segments(clean_nsid)

    if not re.search(_NSID_VALID_CHARS_REGEX, clean_nsid):
        raise InvalidNsidError('NSID contains invalid chars')

    if len(clean_nsid) > _MAX_NSID_LEN:
        raise InvalidNsidError(f'NSID is too long. Max len: {_MAX_NSID_LEN}')

    if len(segments) < _MIN_NSID_SEGMENTS_COUNT:
        raise InvalidNsidError(f'NSID must contain at least {_MIN_NSID_SEGMENTS_COUNT} segments')

    segments_count = len(clean_segments)
    for segment_index, segment in enumerate(clean_segments):
        is_last_segment = segment_index + 1 == segments_count
        _validate_nsid_segment(segment, is_last_segment)

    return True


def validate_nsid(nsid: str, *, soft_fail: bool = False) -> bool:
    """Validate NSID.

    Args:
        nsid: NSID to validate.
        soft_fail: enable to return False on fall instead of exception

    Returns:
        :obj:`bool`: Validation result.

    Raises:
        :class:`atproto.exceptions.InvalidNsidError`: Invalid NSID exception.
    """

    try:
        return _validate_nsid(nsid)
    except InvalidNsidError as e:
        if soft_fail:
            return False

        raise e

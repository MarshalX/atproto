import re
from dataclasses import dataclass, field
from typing import List

from exceptions import InvalidNsidError

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

Segments = List[str]


@dataclass
class NSID:
    segments: Segments = field(default_factory=list)

    @classmethod
    def from_str(cls, nsid: str):
        validate_nsid(nsid)
        return cls(segments=get_nsid_segments(nsid))

    @property
    def authority(self) -> str:
        """Authority of NSID

        com.example.thing
        ^^^^^^^^^^^--------> example.com

        delim joined self.segments[:-1][::-1]
        """
        segments_without_name = self.segments[:-1]
        segments_without_name.reverse()

        return _NSID_DELIM.join(segments_without_name)

    @property
    def name(self) -> str:
        return self.segments[-1]


def get_nsid_segments(nsid: str) -> Segments:
    return nsid.split('.')


def _exclude_nsid_namespace_if_exists(segments: Segments) -> str:
    last_segment = segments[-1]

    if last_segment == _NSID_NAMESPACE:
        segments = segments[:-1]

    return _NSID_DELIM.join(segments)


def _validate_nsid_segment(segment: str, is_last_segment: bool) -> bool:
    """Validate NSID segment. Returns True if valid. Raises InvalidNsidError otherwise."""

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
    """Validate NSID. Returns True if valid. Raises InvalidNsidError otherwise."""

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
    """Validate NSID. Returns True if valid. Raises InvalidNsidError otherwise.

    Note:
        enable soft_fail to return False if not valid.
    """
    try:
        return _validate_nsid(nsid)
    except InvalidNsidError as e:
        if soft_fail:
            return False

        raise e


if __name__ == '__main__':
    assert validate_nsid('com.atproto.repo-.*', soft_fail=True) is False
    assert validate_nsid('com.atproto', soft_fail=True) is False
    assert validate_nsid('com.atproto' + '.test' * 90, soft_fail=True) is False
    assert validate_nsid('com.atproto.repo.getRecord', soft_fail=True) is True
    assert validate_nsid('com.atproto.1repo.getRecord', soft_fail=True) is False
    assert validate_nsid('com.atproto.repo1.getRecord', soft_fail=True) is True

    nsid_obj = NSID.from_str('com.atproto.repo.getRecord')
    assert nsid_obj.segments == ['com', 'atproto', 'repo', 'getRecord']
    assert nsid_obj.authority == 'repo.atproto.com'
    assert nsid_obj.name == 'getRecord'

import pytest
from atproto_core.nsid import NSID, validate_nsid

from tests.interop_test_files import get_test_cases


def test_nsid_from_str() -> None:
    nsid_obj = NSID.from_str('com.atproto.repo.getRecord')
    assert nsid_obj.segments == ['com', 'atproto', 'repo', 'getRecord']
    assert nsid_obj.authority == 'repo.atproto.com'
    assert nsid_obj.name == 'getRecord'


@pytest.mark.parametrize('nsid', get_test_cases('nsid_syntax_valid.txt'))
def test_nsid_validation_with_valid(nsid: str) -> None:
    assert validate_nsid(nsid, soft_fail=True) is True


@pytest.mark.parametrize('nsid', get_test_cases('nsid_syntax_invalid.txt'))
def test_nsid_validation_with_invalid(nsid: str) -> None:
    assert validate_nsid(nsid, soft_fail=True) is False

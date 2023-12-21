from atproto_core.nsid import NSID, validate_nsid


def test_nsid_from_str() -> None:
    nsid_obj = NSID.from_str('com.atproto.repo.getRecord')
    assert nsid_obj.segments == ['com', 'atproto', 'repo', 'getRecord']
    assert nsid_obj.authority == 'repo.atproto.com'
    assert nsid_obj.name == 'getRecord'


def test_nsid_validation() -> None:
    assert validate_nsid('com.atproto.repo-.*', soft_fail=True) is False
    assert validate_nsid('com.atproto', soft_fail=True) is False
    assert validate_nsid('com.atproto' + '.test' * 90, soft_fail=True) is False
    assert validate_nsid('com.atproto.repo.getRecord', soft_fail=True) is True
    assert validate_nsid('com.atproto.1repo.getRecord', soft_fail=True) is False
    assert validate_nsid('com.atproto.repo1.getRecord', soft_fail=True) is True

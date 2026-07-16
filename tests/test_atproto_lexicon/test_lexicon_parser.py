import shutil
from pathlib import Path

from atproto_lexicon.parser import _PATH_TO_LEXICONS, lexicon_parse_file, lexicon_parse_dir  # noqa


def test_lexicon_parse_file() -> None:
    lexicon_parse_file(_PATH_TO_LEXICONS.joinpath('app.bsky.actor.profile.json'))


def test_lexicon_parse_dir() -> None:
    lexicon_parse_dir(_PATH_TO_LEXICONS)


def test_lexicon_parse_dir_with_subdirectories(tmp_path: Path) -> None:
    shutil.copy(_PATH_TO_LEXICONS.joinpath('app.bsky.actor.profile.json'), tmp_path)
    nested_dir = tmp_path.joinpath('app', 'bsky', 'feed')
    nested_dir.mkdir(parents=True)
    shutil.copy(_PATH_TO_LEXICONS.joinpath('app.bsky.feed.post.json'), nested_dir)

    parsed_lexicons = lexicon_parse_dir(tmp_path)

    parsed_ids = {lexicon.id for lexicon in parsed_lexicons}
    assert parsed_ids == {'app.bsky.actor.profile', 'app.bsky.feed.post'}

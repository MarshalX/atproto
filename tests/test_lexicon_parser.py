from atproto.lexicon.parser import _PATH_TO_LEXICONS, lexicon_parse_file, lexicon_parse_dir  # noqa


def test_lexicon_parse_file():
    lexicon_parse_file(_PATH_TO_LEXICONS.joinpath('app.bsky.actor.profile.json'))


def test_lexicon_parse_dir():
    lexicon_parse_dir(_PATH_TO_LEXICONS)

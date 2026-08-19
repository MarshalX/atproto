import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from update_changelog import _clean_body, _linkify


def test_own_repo_pull_url_becomes_a_short_reference() -> None:
    body = 'Add stuff by @MarshalX in https://github.com/MarshalX/atproto/pull/704'

    assert _linkify(body) == (
        'Add stuff by [@MarshalX](https://github.com/MarshalX) in [#704](https://github.com/MarshalX/atproto/pull/704)'
    )


def test_foreign_repo_pull_url_keeps_the_repo_in_the_label() -> None:
    body = 'See https://github.com/bluesky-social/atproto/pull/42'

    assert _linkify(body) == 'See [bluesky-social/atproto#42](https://github.com/bluesky-social/atproto/pull/42)'


def test_issue_urls_are_linked_too() -> None:
    body = 'Fixes https://github.com/MarshalX/atproto/issues/13'

    assert _linkify(body) == 'Fixes [#13](https://github.com/MarshalX/atproto/issues/13)'


def test_every_url_of_a_multi_pull_line_is_linked() -> None:
    body = 'Update lexicons in https://github.com/MarshalX/atproto/pull/691 and https://github.com/MarshalX/atproto/pull/698'

    assert _linkify(body) == (
        'Update lexicons in [#691](https://github.com/MarshalX/atproto/pull/691) '
        'and [#698](https://github.com/MarshalX/atproto/pull/698)'
    )


def test_already_linked_urls_and_mentions_are_left_alone() -> None:
    body = 'By [@MarshalX](https://github.com/MarshalX) in [#704](https://github.com/MarshalX/atproto/pull/704)'

    assert _linkify(body) == body


def test_bold_marker_after_a_url_is_not_swallowed() -> None:
    body = '**More info: https://github.com/MarshalX/atproto/pull/704**'

    assert _linkify(body) == '**More info: [#704](https://github.com/MarshalX/atproto/pull/704)**'


def test_non_pull_urls_are_untouched() -> None:
    body = 'Docs: https://atproto.blue/en/latest/dm.html'

    assert _linkify(body) == body


def test_clean_body_strips_scaffolding_and_links() -> None:
    body = (
        "## What's Changed\r\n"
        '* Add stuff by @MarshalX in https://github.com/MarshalX/atproto/pull/704\r\n'
        '\r\n'
        '**Full Changelog**: https://github.com/MarshalX/atproto/compare/v0.0.69...v0.0.70\r\n'
    )

    assert _clean_body(body) == (
        '* Add stuff by [@MarshalX](https://github.com/MarshalX) in [#704](https://github.com/MarshalX/atproto/pull/704)'
    )


def test_bot_mention_links_to_the_app_page() -> None:
    body = 'Bump h11 by @dependabot[bot]'

    assert _linkify(body) == 'Bump h11 by [@dependabot[bot]](https://github.com/apps/dependabot)'

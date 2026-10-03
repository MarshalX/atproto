"""Tests for facet detection.

Ported from the TypeScript SDK: https://github.com/bluesky-social/atproto/blob/main/packages/api/tests/rich-text-detection.test.ts
with some additional tests added to verify ported behaviour.
"""

import typing as t

import pytest
from atproto_client import models
from atproto_client.utils import facet_detection

BS = chr(92)
ZWSP = chr(0x200B)
VS16 = chr(0xFE0F)
KEYCAP = chr(0x20E3)
COMBINING_ENCLOSING = chr(0x20E2)
FULL_WIDTH_HASH = chr(0xFF03)
E_ACUTE = chr(0xE9)
FAMILY = '👨‍👩‍👧‍👧'
HASH_KEYCAP = '#' + VS16 + KEYCAP

_LINK_THING = 'https://foo.com/thing_(cool)'


def _sliced(text: str, facet: models.AppBskyRichtextFacet.Main) -> str:
    return text.encode('UTF-8')[facet.index.byte_start : facet.index.byte_end].decode('UTF-8')


def _links(text: str) -> t.List[t.Tuple[str, str]]:
    """Return (text of the slice, uri) of every link facet."""
    result = []
    for facet in facet_detection.detect_facets(text):
        for feature in facet.features:
            if isinstance(feature, models.AppBskyRichtextFacet.Link):
                result.append((_sliced(text, facet), feature.uri))
    return result


def _tags(text: str, *, cashtags: bool = False) -> t.Tuple[t.List[str], t.List[t.Tuple[int, int]]]:
    """Return tags and byte indices of every tag facet (cashtags are tags starting with $)."""
    tags, indices = [], []
    for facet in facet_detection.detect_facets(text):
        for feature in facet.features:
            if isinstance(feature, models.AppBskyRichtextFacet.Tag) and feature.tag.startswith('$') == cashtags:
                tags.append(feature.tag)
                indices.append((facet.index.byte_start, facet.index.byte_end))
    return tags, indices


@pytest.mark.parametrize(
    ('text', 'expected'),
    [
        ('no link', []),
        ('start https://middle.com end', [('https://middle.com', 'https://middle.com')]),
        ('start https://middle.com/foo/bar end', [('https://middle.com/foo/bar',) * 2]),
        ('start https://middle.com/foo/bar?baz=bux end', [('https://middle.com/foo/bar?baz=bux',) * 2]),
        (
            'start https://middle.com/foo/bar?baz=bux#hash end',
            [('https://middle.com/foo/bar?baz=bux#hash',) * 2],
        ),
        (
            'https://start.com/foo/bar?baz=bux#hash middle end',
            [('https://start.com/foo/bar?baz=bux#hash',) * 2],
        ),
        (
            'start middle https://end.com/foo/bar?baz=bux#hash',
            [('https://end.com/foo/bar?baz=bux#hash',) * 2],
        ),
        (
            'https://newline1.com\nhttps://newline2.com',
            [('https://newline1.com',) * 2, ('https://newline2.com',) * 2],
        ),
        (f'{FAMILY} https://middle.com {FAMILY}', [('https://middle.com',) * 2]),
        # no scheme
        ('start middle.com end', [('middle.com', 'https://middle.com')]),
        ('start middle.com/foo/bar end', [('middle.com/foo/bar', 'https://middle.com/foo/bar')]),
        (
            'start middle.com/foo/bar?baz=bux end',
            [('middle.com/foo/bar?baz=bux', 'https://middle.com/foo/bar?baz=bux')],
        ),
        (
            'start middle.com/foo/bar?baz=bux#hash end',
            [('middle.com/foo/bar?baz=bux#hash', 'https://middle.com/foo/bar?baz=bux#hash')],
        ),
        (
            'start.com/foo/bar?baz=bux#hash middle end',
            [('start.com/foo/bar?baz=bux#hash', 'https://start.com/foo/bar?baz=bux#hash')],
        ),
        (
            'start middle end.com/foo/bar?baz=bux#hash',
            [('end.com/foo/bar?baz=bux#hash', 'https://end.com/foo/bar?baz=bux#hash')],
        ),
        (
            'newline1.com\nnewline2.com',
            [('newline1.com', 'https://newline1.com'), ('newline2.com', 'https://newline2.com')],
        ),
        ('a example.com/index.php php link', [('example.com/index.php', 'https://example.com/index.php')]),
        ('a trailing bsky.app: colon', [('bsky.app', 'https://bsky.app')]),
        # a domain without a scheme needs a known TLD, which is checked case-sensitively (like the TypeScript SDK)
        ('see example.xyzzy now', []),
        ('see a.b.c.dev/x?y=1 now', [('a.b.c.dev/x?y=1', 'https://a.b.c.dev/x?y=1')]),
        ('see (bsky.app/profile) ok', [('bsky.app/profile', 'https://bsky.app/profile')]),
        ('see EXAMPLE.com now', [('EXAMPLE.com', 'https://EXAMPLE.com')]),
        ('see Example.COM now', []),
        ('see example.COM now', []),
        # the scheme is case-sensitive too
        ('see HTTPS://example.com now', []),
        # Improvement on TypeScript SDK - domains w/o schemes starting with "http" are not mistaken for full URLs
        ('try httpbin.org now', [('httpbin.org', 'https://httpbin.org')]),
        ('try httpbin.org/get?a=b now', [('httpbin.org/get?a=b', 'https://httpbin.org/get?a=b')]),
        ('try https://httpbin.org now', [('https://httpbin.org', 'https://httpbin.org')]),
        ('try httpfoo.xyzzy now', []),
        # not links
        ('not.. a..url ..here', []),
        ('e.g.', []),
        ('something-cool.jpg', []),
        ('website.com.jpg', []),
        ('e.g./foo', []),
        ('website.com.jpg/foo', []),
        # trailing punctuation
        (
            'Classic article https://socket3.wordpress.com/2018/02/03/designing-windows-95s-user-interface/',
            [('https://socket3.wordpress.com/2018/02/03/designing-windows-95s-user-interface/',) * 2],
        ),
        (
            'Classic article https://socket3.wordpress.com/2018/02/03/designing-windows-95s-user-interface/ ',
            [('https://socket3.wordpress.com/2018/02/03/designing-windows-95s-user-interface/',) * 2],
        ),
        (
            'https://foo.com https://bar.com/whatever https://baz.com',
            [('https://foo.com',) * 2, ('https://bar.com/whatever',) * 2, ('https://baz.com',) * 2],
        ),
        (
            'punctuation https://foo.com, https://bar.com/whatever; https://baz.com.',
            [('https://foo.com',) * 2, ('https://bar.com/whatever',) * 2, ('https://baz.com',) * 2],
        ),
        ('parenthentical (https://foo.com)', [('https://foo.com',) * 2]),
        (f'except for {_LINK_THING}', [(_LINK_THING,) * 2]),
    ],
)
def test_detect_links(text: str, expected: t.List[t.Tuple[str, str]]) -> None:
    assert _links(text) == expected


_TAG_CASES: t.List[t.Tuple[str, t.List[str], t.List[t.Tuple[int, int]]]] = [
    ('#a', ['a'], [(0, 2)]),
    ('#a #b', ['a', 'b'], [(0, 2), (3, 5)]),
    ('#1', [], []),
    ('#1a', ['1a'], [(0, 3)]),
    ('#tag', ['tag'], [(0, 4)]),
    ('body #tag', ['tag'], [(5, 9)]),
    ('#tag body', ['tag'], [(0, 4)]),
    ('body #tag body', ['tag'], [(5, 9)]),
    ('body #1', [], []),
    ('body #1a', ['1a'], [(5, 8)]),
    ('body #a1', ['a1'], [(5, 8)]),
    ('#', [], []),
    ('#?', [], []),
    ('text #', [], []),
    ('text # text', [], []),
    (
        'body #thisisa64characterstring_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        ['thisisa64characterstring_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'],
        [(5, 70)],
    ),
    ('body #thisisa65characterstring_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaab', [], []),
    (
        'body #thisisa64characterstring_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa!',
        ['thisisa64characterstring_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'],
        [(5, 70)],
    ),
    ('its a #double#rainbow', ['double#rainbow'], [(6, 21)]),
    ('##hashash', ['#hashash'], [(0, 9)]),
    ('##', [], []),
    ('some #n0n3s@n5e!', ['n0n3s@n5e'], [(5, 15)]),
    ('works #with,punctuation', ['with,punctuation'], [(6, 23)]),
    (
        'strips trailing #punctuation, #like. #this!',
        ['punctuation', 'like', 'this'],
        [(16, 28), (30, 35), (37, 42)],
    ),
    ('strips #multi_trailing___...', ['multi_trailing'], [(7, 22)]),
    ('works with #🦋 emoji, and #butter🦋fly', ['🦋', 'butter🦋fly'], [(11, 16), (28, 42)]),
    ('#same #same #but #diff', ['same', 'same', 'but', 'diff'], [(0, 5), (6, 11), (12, 16), (17, 22)]),
    (f'this {HASH_KEYCAP}tag should not be a tag', [], []),
    (f'this #{HASH_KEYCAP}tag should be a tag', [HASH_KEYCAP + 'tag'], [(5, 16)]),
    ('this #t\nag should be a tag', ['t'], [(5, 7)]),
    # the first two have a literal backslash-u sequence in the text, the last char is a real zero-width space
    (f'no match ({BS}u200B): #{ZWSP}', [], []),
    (f'no match ({BS}u200Ba): #{ZWSP}a', [], []),
    (f'match (a{BS}u200Bb): #a{ZWSP}b', ['a'], [(18, 20)]),
    (f'match (ab{BS}u200B): #ab{ZWSP}', ['ab'], [(18, 21)]),
    (f'no match ({BS}u20e2tag): #{COMBINING_ENCLOSING}tag', [], []),
    (f'no match (a{BS}u20e2b): #a{COMBINING_ENCLOSING}b', ['a'], [(21, 23)]),
    (f'match full width number sign (tag): {FULL_WIDTH_HASH}tag', ['tag'], [(36, 42)]),
    (
        f'match full width number sign (tag): {FULL_WIDTH_HASH}{HASH_KEYCAP}tag',
        [HASH_KEYCAP + 'tag'],
        [(36, 49)],
    ),
    ('no match 1?: #1?', [], []),
    # TypeScript to Python compatibility tests
    ('#c++ rocks', ['c++'], [(0, 4)]),
    ('#2+2=4', ['2+2=4'], [(0, 6)]),
    ('I love #tag^', ['tag^'], [(7, 12)]),
    ('#tag`', ['tag`'], [(0, 5)]),
    ('#price$', ['price$'], [(0, 7)]),
    ('#tag~', ['tag~'], [(0, 5)]),
    ('#a|b', ['a|b'], [(0, 4)]),
    ('#tag。', ['tag'], [(0, 4)]),
    ('#café”', ['café'], [(0, 6)]),
    ('#tag—', ['tag'], [(0, 4)]),
    ('「#tag」', [], []),
]


@pytest.mark.parametrize(('text', 'tags', 'indices'), _TAG_CASES)
def test_detect_tags(text: str, tags: t.List[str], indices: t.List[t.Tuple[int, int]]) -> None:
    assert _tags(text) == (tags, indices)


# Each is a single grapheme made of several code points.
_MULTI_CODE_POINT_GRAPHEMES: t.Dict[str, str] = {
    'thai': chr(0x0E01) + chr(0x0E33),  # consonant + sara am (กำ)
    'devanagari': chr(0x0915) + chr(0x094D) + chr(0x0937),  # ka + virama + ssa (क्ष)
    'hangul_jamo': chr(0x1112) + chr(0x1161) + chr(0x11AB),  # choseong + jungseong + jongseong (한)
}


@pytest.mark.xfail(strict=True, reason='_grapheme_len currently overcounts these graphemes')
@pytest.mark.parametrize('grapheme', _MULTI_CODE_POINT_GRAPHEMES.values(), ids=_MULTI_CODE_POINT_GRAPHEMES.keys())
def test_detect_tags_at_the_grapheme_limit_with_multiple_code_points(grapheme: str) -> None:
    tag = grapheme * 64
    assert _tags(f'body #{tag}') == ([tag], [(5, 5 + 1 + len(tag.encode()))])


@pytest.mark.parametrize('grapheme', _MULTI_CODE_POINT_GRAPHEMES.values(), ids=_MULTI_CODE_POINT_GRAPHEMES.keys())
def test_detect_tags_over_the_grapheme_limit_with_multiple_code_points(grapheme: str) -> None:
    assert _tags(f'body #{grapheme * 65}') == ([], [])


_CASHTAG_CASES: t.List[t.Tuple[str, t.List[str], t.List[t.Tuple[int, int]]]] = [
    ('$AAPL', ['$AAPL'], [(0, 5)]),
    ('$aapl', ['$AAPL'], [(0, 5)]),  # normalized to uppercase
    ('$A', ['$A'], [(0, 2)]),
    ('$a', ['$A'], [(0, 2)]),  # single char normalized
    ('$BTC $ETH', ['$BTC', '$ETH'], [(0, 4), (5, 9)]),
    ('$100', [], []),  # starts with digit - not a cashtag
    ('$GOOGL', ['$GOOGL'], [(0, 6)]),  # 5 chars - max length
    ('$TOOLONG', [], []),  # >5 chars
    ('check $LEGO now', ['$LEGO'], [(6, 11)]),
    ('($GOOG)', ['$GOOG'], [(1, 6)]),
    ('$AAPL.', ['$AAPL'], [(0, 5)]),  # trailing punctuation
    ('$AAPL, $MSFT!', ['$AAPL', '$MSFT'], [(0, 5), (7, 12)]),
    ('no$SPACE', [], []),  # must have leading space or start
    ('$', [], []),  # just dollar sign
    ('$ AAPL', [], []),  # space after $
    ('$123ABC', [], []),  # starts with digit
    ('$ABC12', ['$ABC12'], [(0, 6)]),  # digits after letters OK (5 chars)
    ('$ABC123', [], []),  # 6 chars - too long
]


@pytest.mark.parametrize(('text', 'tags', 'indices'), _CASHTAG_CASES)
def test_detect_cashtags(text: str, tags: t.List[str], indices: t.List[t.Tuple[int, int]]) -> None:
    assert _tags(text, cashtags=True) == (tags, indices)


def test_detect_facets_without_facets() -> None:
    assert facet_detection.detect_facets('') == []
    assert facet_detection.detect_facets('nothing to see here') == []


def test_detect_facets_sorted_by_position() -> None:
    text = '$AAPL #tag https://example.com'

    facets = facet_detection.detect_facets(text)

    assert [_sliced(text, facet) for facet in facets] == ['$AAPL', '#tag', 'https://example.com']
    assert isinstance(facets[0].features[0], models.AppBskyRichtextFacet.Tag)
    assert isinstance(facets[1].features[0], models.AppBskyRichtextFacet.Tag)
    assert isinstance(facets[2].features[0], models.AppBskyRichtextFacet.Link)


def test_detect_facets_uses_utf8_byte_indices() -> None:
    text = f'{FAMILY} #tag'

    (facet,) = facet_detection.detect_facets(text)

    assert facet.index.byte_start == len(f'{FAMILY} '.encode())
    assert _sliced(text, facet) == '#tag'


def _mentions(text: str) -> t.List[str]:
    """Return the handles of all detected mentions. Checks that the byte range of each is `@handle`."""
    handles = []
    for mention in facet_detection.detect_mentions(text):
        assert text.encode()[mention.byte_start : mention.byte_end].decode() == f'@{mention.handle}'
        handles.append(mention.handle)
    return handles


@pytest.mark.parametrize(
    ('text', 'handles'),
    [
        ('no mention', []),
        ('@handle.com middle end', ['handle.com']),
        ('start @handle.com end', ['handle.com']),
        ('start middle @handle.com', ['handle.com']),
        ('@handle.com @handle.com @handle.com', ['handle.com'] * 3),
        ('@full123-chars.test', ['full123-chars.test']),
        ('not@right', []),
        ('@handle.com!@#$chars', ['handle.com']),
        ('@handle.com\n@handle.com', ['handle.com'] * 2),
        ('parenthetical (@handle.com)', ['handle.com']),
        (f'{FAMILY} @handle.com {FAMILY}', ['handle.com']),
        # Not in the TS tests, but checked against the TypeScript SDK
        ('@handle.com.', ['handle.com']),
        ('@handle.com...', ['handle.com']),
        (f'@handle.com{E_ACUTE}', ['handle.com']),  # a word boundary is ASCII only
        (f'@handle.co{E_ACUTE}', ['handle.co']),
        ('@a.b.c.dev', ['a.b.c.dev']),
        ('@handle-.com', ['handle-.com']),
        ('@.com', ['.com']),
        ('foo@handle.com', []),
        ('https://example.com/@handle.com', []),
        ('@@handle.com', []),
        # the handle has to end with a known TLD (or .test), which is case-sensitive
        ('@nodot', []),
        ('@com', []),
        ('@handle.xyzzy', []),
        ('@handle.test', ['handle.test']),
        ('@test', []),
        ('@HANDLE.com', ['HANDLE.com']),
        ('@Handle.COM', []),
        ('@handle.COM', []),
        ('@handle.TEST', []),
    ],
)
def test_detect_mentions(text: str, handles: t.List[str]) -> None:
    assert _mentions(text) == handles


def test_detect_mentions_uses_utf8_byte_indices() -> None:
    (mention,) = facet_detection.detect_mentions(f'{FAMILY} @handle.com')

    assert mention.handle == 'handle.com'
    assert mention.byte_start == len(f'{FAMILY} '.encode())
    assert mention.byte_end == mention.byte_start + len('@handle.com')

import typing as t
import unicodedata

from atproto_client import models
from atproto_client.utils.facet_regexes import (
    CASHTAG_REGEX,
    MENTION_REGEX,
    TAG_REGEX,
    TRAILING_PUNCTUATION_REGEX,
    URL_REGEX,
)
from atproto_client.utils.tlds import TLDS

# Ported from `detectFacets` of the TypeScript SDK (@atproto/api):
# https://github.com/bluesky-social/atproto/blob/main/packages/api/src/rich-text/detection.ts

_MAX_TAG_GRAPHEMES = 64

_FacetFeature = t.Union[
    models.AppBskyRichtextFacet.Link,
    models.AppBskyRichtextFacet.Tag,
]


def _grapheme_len(text: str) -> int:
    """Approximate the number of user-perceived characters (graphemes) in the text.

    Python's standard library can't segment grapheme clusters, so this counts code points
    and skips the ones that don't start a new cluster: combining marks, variation selectors,
    emoji skin tone modifiers, tag characters, and whatever follows a zero width joiner.
    A pair of regional indicators (a flag) counts as one.

    This isn't a perfect implementation of UAX #29 (https://www.unicode.org/reports/tr29/),
    but it is an improvement on using a simple len(str).

    Fallback package used by `@atproto/api`: https://github.com/cometkim/unicode-segmenter
    """
    count = 0
    after_joiner = False
    pending_regional_indicator = False

    for char in text:
        code_point = ord(char)

        if after_joiner:
            after_joiner = False
            continue
        if code_point == 0x200D:  # zero width joiner
            after_joiner = True
            continue
        if (
            unicodedata.category(char) in ('Mn', 'Mc', 'Me')
            or 0x1F3FB <= code_point <= 0x1F3FF
            or 0xE0020 <= code_point <= 0xE007F
        ):
            continue

        if 0x1F1E6 <= code_point <= 0x1F1FF:
            pending_regional_indicator = not pending_regional_indicator
            if not pending_regional_indicator:
                continue

        count += 1

    return count


def _get_utf8_byte_index(text: str, index: int) -> int:
    """Convert an index in the string (code points) to an index in its UTF-8 encoding (bytes)."""
    return len(text[:index].encode('UTF-8'))


def _create_facet(text: str, start: int, end: int, feature: _FacetFeature) -> models.AppBskyRichtextFacet.Main:
    return models.AppBskyRichtextFacet.Main(
        features=[feature],
        index=models.AppBskyRichtextFacet.ByteSlice(
            byte_start=_get_utf8_byte_index(text, start),
            byte_end=_get_utf8_byte_index(text, end),
        ),
    )


def _is_valid_domain(domain: str) -> bool:
    """Check that the domain ends with a known TLD (case-sensitive, like in the TypeScript SDK)."""
    _, dot, tld = domain.rpartition('.')
    return bool(dot) and tld in TLDS


def _detect_links(text: str) -> t.List[models.AppBskyRichtextFacet.Main]:
    facets = []

    for match in URL_REGEX.finditer(text):
        uri = match.group(2)
        start, end = match.span(2)

        if not uri.startswith('http'):
            domain = match.group('domain')
            if not domain or not _is_valid_domain(domain):
                continue

            uri = f'https://{uri}'

        # strip ending punctuation
        if uri[-1] in '.,;:!?':
            uri = uri[:-1]
            end -= 1
        if uri.endswith(')') and '(' not in uri:
            uri = uri[:-1]
            end -= 1

        facets.append(_create_facet(text, start, end, models.AppBskyRichtextFacet.Link(uri=uri)))

    return facets


def _detect_tags(text: str) -> t.List[models.AppBskyRichtextFacet.Main]:
    facets = []

    for match in TAG_REGEX.finditer(text):
        tag = match.group(2)
        if not tag:
            continue

        # strip ending punctuation
        tag = TRAILING_PUNCTUATION_REGEX.sub('', tag)

        # Python's len(str) is always >= the number of graphemes, so only
        # pay for counting graphemes when the tag is longer than the limit.
        if not tag or (len(tag) > _MAX_TAG_GRAPHEMES and _grapheme_len(tag) > _MAX_TAG_GRAPHEMES):
            continue

        start = match.end(1)  # Hashtag character (#) position
        facets.append(_create_facet(text, start, start + 1 + len(tag), models.AppBskyRichtextFacet.Tag(tag=tag)))

    return facets


def _detect_cashtags(text: str) -> t.List[models.AppBskyRichtextFacet.Main]:
    facets = []

    for match in CASHTAG_REGEX.finditer(text):
        ticker = match.group(2).upper()  # normalize to uppercase

        start = match.end(1)  # Dollar sign ($) position
        facets.append(
            _create_facet(
                text,
                start,
                start + 1 + len(ticker),
                models.AppBskyRichtextFacet.Tag(tag='$' + ticker),  # stored with the dollar sign
            )
        )

    return facets


def detect_facets(text: str) -> t.List[models.AppBskyRichtextFacet.Main]:
    """Detect non-@mention facets in the text: links, #tags and $cashtags.

    Args:
        text: Text to detect facets in.

    Returns:
        Detected facets sorted by their position in the text.
    """
    facets = [*_detect_links(text), *_detect_tags(text), *_detect_cashtags(text)]
    return sorted(facets, key=lambda facet: facet.index.byte_start)


class MentionMatch(t.NamedTuple):
    """A mention found in the text. The handle is not resolved to a DID."""

    handle: str  #: Handle without the ``@``.
    byte_start: int  #: Start of the ``@handle`` in the UTF-8 encoded text (inclusive).
    byte_end: int  #: End of the ``@handle`` in the UTF-8 encoded text (exclusive).


def detect_mentions(text: str) -> t.List[MentionMatch]:
    """Detect mentions (e.g. ``@bsky.app``) in the text.

    This function doesn't make any network requests, so handles
    are not resolved to DIDs and it can't tell if they exist.

    Args:
        text: Text to detect mentions in.

    Returns:
        Detected mentions in the order they appear in the text.
    """
    mentions = []

    for match in MENTION_REGEX.finditer(text):
        handle = match.group(3)
        if not _is_valid_domain(handle) and not handle.endswith('.test'):
            continue  # probably not a handle

        start = match.end(1)  # At sign (@) position
        mentions.append(
            MentionMatch(
                handle=handle,
                byte_start=_get_utf8_byte_index(text, start),
                byte_end=_get_utf8_byte_index(text, match.end(3)),
            )
        )

    return mentions

r"""Regular expressions for detecting facets in text.

Ported from the ``@atproto/api`` TypeScript SDK:
https://github.com/bluesky-social/atproto/blob/main/packages/api/src/rich-text/util.ts

The goal is to match the behaviour of the TypeScript regexes as closely as possible.
``re`` differs from TypeScript in a few places:

* ``\s`` and ``\p{P}`` are written as explicit character classes (see ``_S`` and ``_P``)
* ``\d`` is written ``0-9``, because in Python it matches every Unicode digit
* ``$`` is written ``\Z``, because in Python it also matches before a trailing newline
* ``re.IGNORECASE`` matches the ``i`` flag, with ``re.ASCII`` added so case folding stays ASCII only (as in TypeScript)
* ``\b`` is ASCII only in TypeScript, so the mention regex uses ``re.ASCII`` too
"""

import re

# Whitespace - TypeScript's `\s`
#
# Using an explicit match, because Python's native `\s` has two issues:
# * Minor: `\s` also matches `\x1c-\x1f` and `\x85`, and not `\ufeff` (rare control/format chars)
# * Major: with `re.ASCII` (URL/mention regexes) `\s` is ASCII-only, so Unicode spaces (e.g. `\u3000`) aren't matched
_S = r'\t\n\v\f\r \u00a0\u1680\u2000-\u200a\u2028\u2029\u202f\u205f\u3000\ufeff'

# Punctuation - TypeScript's `\p{P}`
#
# `re` doesn't have an equivalent to TypeScript's Unicode punctuation selector `\p{P}`.
# So here an explicit list of all Unicode punctuation code points is created
# (every code point whose category starts with ``P`` as of Unicode 16.0.0).
_P = (
    r'\u0021-\u0023\u0025-\u002a\u002c-\u002f\u003a-\u003b\u003f-\u0040\u005b-\u005d\u005f\u007b\u007d'
    r'\u00a1\u00a7\u00ab\u00b6-\u00b7\u00bb\u00bf\u037e\u0387\u055a-\u055f\u0589-\u058a\u05be\u05c0\u05c3'
    r'\u05c6\u05f3-\u05f4\u0609-\u060a\u060c-\u060d\u061b\u061d-\u061f\u066a-\u066d\u06d4\u0700-\u070d'
    r'\u07f7-\u07f9\u0830-\u083e\u085e\u0964-\u0965\u0970\u09fd\u0a76\u0af0\u0c77\u0c84\u0df4\u0e4f'
    r'\u0e5a-\u0e5b\u0f04-\u0f12\u0f14\u0f3a-\u0f3d\u0f85\u0fd0-\u0fd4\u0fd9-\u0fda\u104a-\u104f\u10fb'
    r'\u1360-\u1368\u1400\u166e\u169b-\u169c\u16eb-\u16ed\u1735-\u1736\u17d4-\u17d6\u17d8-\u17da'
    r'\u1800-\u180a\u1944-\u1945\u1a1e-\u1a1f\u1aa0-\u1aa6\u1aa8-\u1aad\u1b4e-\u1b4f\u1b5a-\u1b60'
    r'\u1b7d-\u1b7f\u1bfc-\u1bff\u1c3b-\u1c3f\u1c7e-\u1c7f\u1cc0-\u1cc7\u1cd3\u2010-\u2027\u2030-\u2043'
    r'\u2045-\u2051\u2053-\u205e\u207d-\u207e\u208d-\u208e\u2308-\u230b\u2329-\u232a\u2768-\u2775'
    r'\u27c5-\u27c6\u27e6-\u27ef\u2983-\u2998\u29d8-\u29db\u29fc-\u29fd\u2cf9-\u2cfc\u2cfe-\u2cff\u2d70'
    r'\u2e00-\u2e2e\u2e30-\u2e4f\u2e52-\u2e5d\u3001-\u3003\u3008-\u3011\u3014-\u301f\u3030\u303d\u30a0'
    r'\u30fb\ua4fe-\ua4ff\ua60d-\ua60f\ua673\ua67e\ua6f2-\ua6f7\ua874-\ua877\ua8ce-\ua8cf\ua8f8-\ua8fa'
    r'\ua8fc\ua92e-\ua92f\ua95f\ua9c1-\ua9cd\ua9de-\ua9df\uaa5c-\uaa5f\uaade-\uaadf\uaaf0-\uaaf1\uabeb'
    r'\ufd3e-\ufd3f\ufe10-\ufe19\ufe30-\ufe52\ufe54-\ufe61\ufe63\ufe68\ufe6a-\ufe6b\uff01-\uff03'
    r'\uff05-\uff0a\uff0c-\uff0f\uff1a-\uff1b\uff1f-\uff20\uff3b-\uff3d\uff3f\uff5b\uff5d\uff5f-\uff65'
    r'\U00010100-\U00010102\U0001039f\U000103d0\U0001056f\U00010857\U0001091f\U0001093f'
    r'\U00010a50-\U00010a58\U00010a7f\U00010af0-\U00010af6\U00010b39-\U00010b3f\U00010b99-\U00010b9c'
    r'\U00010d6e\U00010ead\U00010f55-\U00010f59\U00010f86-\U00010f89\U00011047-\U0001104d'
    r'\U000110bb-\U000110bc\U000110be-\U000110c1\U00011140-\U00011143\U00011174-\U00011175'
    r'\U000111c5-\U000111c8\U000111cd\U000111db\U000111dd-\U000111df\U00011238-\U0001123d\U000112a9'
    r'\U000113d4-\U000113d5\U000113d7-\U000113d8\U0001144b-\U0001144f\U0001145a-\U0001145b\U0001145d'
    r'\U000114c6\U000115c1-\U000115d7\U00011641-\U00011643\U00011660-\U0001166c\U000116b9'
    r'\U0001173c-\U0001173e\U0001183b\U00011944-\U00011946\U000119e2\U00011a3f-\U00011a46'
    r'\U00011a9a-\U00011a9c\U00011a9e-\U00011aa2\U00011b00-\U00011b09\U00011be1\U00011c41-\U00011c45'
    r'\U00011c70-\U00011c71\U00011ef7-\U00011ef8\U00011f43-\U00011f4f\U00011fff\U00012470-\U00012474'
    r'\U00012ff1-\U00012ff2\U00016a6e-\U00016a6f\U00016af5\U00016b37-\U00016b3b\U00016b44'
    r'\U00016d6d-\U00016d6f\U00016e97-\U00016e9a\U00016fe2\U0001bc9f\U0001da87-\U0001da8b\U0001e5ff'
    r'\U0001e95e-\U0001e95f'
)

MENTION_REGEX = re.compile(
    rf'(^|[{_S}]|\()(@)([a-zA-Z0-9.-]+)(\b)',
    re.ASCII,
)

URL_REGEX = re.compile(
    rf'(^|[{_S}]|\()((https?://[^{_S}]+)|((?P<domain>[a-z][a-z0-9]*(\.[a-z0-9]+)+)[^{_S}]*))',
    re.IGNORECASE | re.MULTILINE | re.ASCII,
)

TRAILING_PUNCTUATION_REGEX = re.compile(rf'[{_P}]+\Z')

# Hardcoded emoji modifier & zero-width spaces (likely incomplete)
_EMOJI = r'\ufe0f'
_ZERO_WIDTH = r'\u00ad\u2060\u200a\u200b\u200c\u200d\u20e2'
TAG_REGEX = re.compile(
    rf'(^|[{_S}])[#＃]((?!{_EMOJI})'  # noqa: RUF001 (allow the full-width hashtag sign here)
    rf'[^{_S}{_ZERO_WIDTH}]*[^0-9{_S}{_P}{_ZERO_WIDTH}]+[^{_S}{_ZERO_WIDTH}]*)?'
)

CASHTAG_REGEX = re.compile(rf'(^|[{_S}]|\()\$([A-Za-z][A-Za-z0-9]{{0,4}})(?=[{_S}]|\Z|[.,;:!?)"\'\u2019])')

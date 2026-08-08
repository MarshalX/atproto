"""Scope string tokenizer.

Parses scope strings of the form ``resource[:positional][?key=val&key=val]``
into structured parts.

Examples::

    ScopeStringSyntax.from_string("repo:fm.plyr.track?action=create")
    # -> prefix="repo", positional="fm.plyr.track", params={"action": ["create"]}

    ScopeStringSyntax.from_string("repo?collection=a.b.c&collection=d.e.f")
    # -> prefix="repo", positional=None, params={"collection": ["a.b.c", "d.e.f"]}
"""

import typing as t
from dataclasses import dataclass, field
from urllib.parse import parse_qs, unquote, urlencode


@dataclass(frozen=True)
class ScopeStringSyntax:
    """Parsed scope string token."""

    prefix: str
    positional: t.Optional[str] = None
    params: t.Dict[str, t.List[str]] = field(default_factory=dict)

    def keys(self) -> t.Iterator[str]:
        """Iterate over parameter keys."""
        yield from self.params

    def get_single(self, key: str) -> t.Union[str, None]:
        """Get a single-value parameter. Returns None if key is absent or has multiple values."""
        values = self.params.get(key)
        if values is None:
            return None
        if len(values) != 1:
            return None
        return values[0]

    def get_multi(self, key: str) -> t.Optional[t.List[str]]:
        """Get a multi-value parameter. Returns None if key is absent."""
        return self.params.get(key)

    def __str__(self) -> str:
        scope = self.prefix

        if self.positional is not None:
            scope += ':' + _normalize_uri_component(_encode_component(self.positional))

        if self.params:
            # Build query string preserving multi-value params
            pairs: t.List[t.Tuple[str, str]] = []
            for key, values in self.params.items():
                for val in values:
                    pairs.append((key, val))
            scope += '?' + _normalize_uri_component(urlencode(pairs))

        return scope

    @classmethod
    def from_string(cls, scope_value: str) -> 'ScopeStringSyntax':
        """Parse a scope string into its components."""
        param_idx = scope_value.find('?')
        colon_idx = scope_value.find(':')
        prefix_end = _min_idx(param_idx, colon_idx)

        # No param or positional
        if prefix_end == -1:
            return cls(prefix=scope_value)

        prefix = scope_value[:prefix_end]

        # Parse positional parameter if present
        positional: t.Optional[str] = None
        if colon_idx != -1:
            if param_idx == -1:
                positional = unquote(scope_value[colon_idx + 1 :])
            elif colon_idx < param_idx:
                positional = unquote(scope_value[colon_idx + 1 : param_idx])
            # else: colon is inside query string, no positional

        # Parse query string if present and non-empty
        params: t.Dict[str, t.List[str]] = {}
        if param_idx != -1 and param_idx < len(scope_value) - 1:
            params = parse_qs(scope_value[param_idx + 1 :], keep_blank_values=False)

        return cls(prefix=prefix, positional=positional, params=params)


def _min_idx(a: int, b: int) -> int:
    """Return the smaller non-negative index, or -1 if both are -1."""
    if a == -1:
        return b
    if b == -1:
        return a
    return min(a, b)


# Characters that encodeURIComponent does NOT encode (besides alphanumeric).
_UNRESERVED_CHARS = frozenset(('-', '_', '.', '!', '~', '*', "'", '(', ')'))

# Additional characters allowed in scope strings without percent-encoding.
_ALLOWED_SCOPE_CHARS = frozenset(':+,@/%')


def _encode_component(value: str) -> str:
    """Percent-encode a string for use in a scope, keeping allowed chars unencoded.

    Mirrors JS ``encodeURIComponent`` which preserves ``A-Z a-z 0-9 - _ . ! ~ * ' ( )``
    plus the additional scope-allowed chars (``:``, ``/``, ``+``, etc.).
    """
    result: t.List[str] = []
    for ch in value:
        if ch.isalnum() or ch in _UNRESERVED_CHARS or ch in _ALLOWED_SCOPE_CHARS:
            result.append(ch)
        else:
            result.append('%{:02X}'.format(ord(ch)))
    return ''.join(result)


# Characters that should be decoded from percent-encoding in scope strings.
# Union of scope-allowed chars and JS encodeURIComponent unreserved chars.
_NORMALIZABLE_CHARS = _ALLOWED_SCOPE_CHARS | _UNRESERVED_CHARS


def _normalize_uri_component(value: str) -> str:
    """Decode percent-encoded chars that are allowed unencoded in scope strings."""
    result: t.List[str] = []
    i = 0
    end = len(value)
    while i < end:
        if value[i] == '%' and i + 2 < end:
            encoded = value[i : i + 3]
            try:
                decoded_char = chr(int(encoded[1:3], 16))
            except ValueError:
                result.append(value[i])
                i += 1
                continue
            if decoded_char in _NORMALIZABLE_CHARS:
                result.append(decoded_char)
                i += 3
            else:
                result.append(encoded.upper())
                i += 3
        else:
            result.append(value[i])
            i += 1
    return ''.join(result)

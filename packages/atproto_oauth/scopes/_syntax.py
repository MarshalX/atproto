import typing as t
from dataclasses import dataclass, field
from urllib.parse import parse_qs, quote, quote_plus, unquote


@dataclass(frozen=True)
class ScopeStringSyntax:
    """Parsed scope string token."""

    prefix: str
    positional: t.Optional[str] = None
    params: t.Dict[str, t.List[str]] = field(default_factory=dict)

    def keys(self) -> t.Iterator[str]:
        yield from self.params

    def get_single(self, key: str) -> t.Optional[str]:
        """Return the value of a parameter, or :obj:`None` when it is absent or has several values."""
        values = self.params.get(key)
        if values is None or len(values) != 1:
            return None

        return values[0]

    def get_multi(self, key: str) -> t.Optional[t.List[str]]:
        return self.params.get(key)

    def __str__(self) -> str:
        scope = self.prefix

        if self.positional is not None:
            scope += ':' + quote(self.positional, safe=_POSITIONAL_SAFE_CHARS)

        if self.params:
            pairs = [(key, value) for key, values in self.params.items() for value in values]
            scope += '?' + '&'.join(f'{_encode_query(key)}={_encode_query(value)}' for key, value in pairs)

        return scope

    @classmethod
    def from_string(cls, scope_value: str) -> 'ScopeStringSyntax':
        """Parse a scope of the form ``resource[:positional][?name=value&name=value]``."""
        param_idx = scope_value.find('?')
        colon_idx = scope_value.find(':')
        prefix_end = _min_idx(param_idx, colon_idx)

        if prefix_end == -1:
            return cls(prefix=scope_value)

        prefix = scope_value[:prefix_end]

        # a colon after the question mark belongs to the query, not to a positional value
        positional: t.Optional[str] = None
        if colon_idx != -1:
            if param_idx == -1:
                positional = unquote(scope_value[colon_idx + 1 :])
            elif colon_idx < param_idx:
                positional = unquote(scope_value[colon_idx + 1 : param_idx])

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


# scopes are compared as strings, so every implementation has to leave the same characters unencoded
_ALLOWED_SCOPE_CHARS: t.Final = ':/+,@%'
_POSITIONAL_SAFE_CHARS: t.Final = "-_.!~*'()" + _ALLOWED_SCOPE_CHARS
_QUERY_SAFE_CHARS: t.Final = '*' + _ALLOWED_SCOPE_CHARS


def _encode_query(value: str) -> str:
    # quote_plus never encodes the tilde, while form encoding does
    return quote_plus(value, safe=_QUERY_SAFE_CHARS).replace('~', '%7E')

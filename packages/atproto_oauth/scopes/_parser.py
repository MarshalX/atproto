import typing as t
from dataclasses import dataclass

from atproto_oauth.scopes._syntax import ScopeStringSyntax


@dataclass(frozen=True)
class ParamSchema:
    multiple: bool
    required: bool
    validate: t.Callable[[str], bool]
    default: t.Any = None
    normalize: t.Optional[t.Callable[..., t.Any]] = None


_INVALID: t.Final = object()


class Parser:
    """Schema-driven scope string parser/formatter.

    Args:
        prefix: The resource type prefix (e.g. ``'repo'``, ``'blob'``).
        schema: Mapping of parameter names to their schemas.
        positional_name: Parameter name that can appear as positional.
    """

    def __init__(
        self,
        prefix: str,
        schema: t.Dict[str, ParamSchema],
        positional_name: t.Optional[str] = None,
    ) -> None:
        self.prefix = prefix
        self.schema = schema
        self.positional_name = positional_name
        self.schema_keys = frozenset(schema)

    def parse(self, syntax: ScopeStringSyntax) -> t.Optional[t.Dict[str, t.Any]]:
        """Parse a syntax object into validated parameter values.

        Returns None on any validation failure (try-parse pattern).
        """
        if not self.schema_keys.issuperset(syntax.keys()):
            return None

        result: t.Dict[str, t.Any] = {}
        for key, defn in self.schema.items():
            value = self._parse_param(key, defn, syntax)
            if value is _INVALID:
                return None

            result[key] = value

        return result

    def _parse_param(self, key: str, defn: ParamSchema, syntax: ScopeStringSyntax) -> t.Any:
        positional = syntax.positional if key == self.positional_name else None
        param = syntax.get_multi(key)

        if param is None:
            if positional is None:
                return _INVALID if defn.required else defn.default

            if not defn.validate(positional):
                return _INVALID

            return [positional] if defn.multiple else positional

        if positional is not None:
            # positional cannot coexist with named
            return _INVALID

        if not param or not all(defn.validate(value) for value in param):
            return _INVALID

        if defn.multiple:
            return param

        # a parameter that takes one value is invalid when given several
        return param[0] if len(param) == 1 else _INVALID

    def format(self, values: t.Dict[str, t.Any]) -> str:
        """Format validated values back into a canonical scope string."""
        params: t.List[t.Tuple[str, str]] = []
        positional: t.Optional[str] = None

        for key, defn in self.schema.items():
            value = values.get(key)
            if value is None:
                continue

            normalized = defn.normalize(value) if defn.normalize else value
            if _is_default(defn, normalized):
                continue

            items = (
                [str(v) for v in t.cast('t.Sequence[t.Any]', normalized)]
                if isinstance(normalized, (list, tuple))
                else None
            )
            if key == self.positional_name and (items is None or len(items) == 1):
                positional = str(normalized) if items is None else items[0]
            elif items is None:
                params.append((key, str(normalized)))
            else:
                params.extend((key, item) for item in dict.fromkeys(items))

        syntax = ScopeStringSyntax(
            prefix=self.prefix,
            positional=positional,
            params=_pairs_to_dict(params) if params else {},
        )
        return str(syntax)


def _is_default(defn: ParamSchema, normalized: t.Any) -> bool:
    if defn.required or defn.default is None:
        return False

    if defn.multiple:
        return _array_param_equals(defn.default, normalized)

    equal: bool = normalized == defn.default
    return equal


def _array_param_equals(a: t.Sequence[t.Any], b: t.Sequence[t.Any]) -> bool:
    """Check if two param arrays contain the same elements (order-independent)."""
    if len(a) != len(b):
        return False

    a_set = {str(x) for x in a}
    b_set = {str(x) for x in b}
    return a_set == b_set


def _pairs_to_dict(pairs: t.List[t.Tuple[str, str]]) -> t.Dict[str, t.List[str]]:
    """Convert a list of key-value pairs into a multi-value dict."""
    result: t.Dict[str, t.List[str]] = {}
    for key, val in pairs:
        result.setdefault(key, []).append(val)

    return result

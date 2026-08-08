"""Generic schema-driven parser for scope parameters.

Each permission type declares a schema dict describing its parameters, then
delegates parsing and formatting to :class:`Parser`.
"""

import typing as t
from dataclasses import dataclass

from atproto_oauth.scopes._syntax import ScopeStringSyntax


@dataclass(frozen=True)
class ParamSchema:
    """Schema for a single parameter."""

    multiple: bool
    required: bool
    validate: t.Callable[[str], bool]
    default: t.Any = None
    normalize: t.Optional[t.Callable[..., t.Any]] = None


class Parser:
    """Schema-driven scope string parser/formatter.

    Args:
        prefix: The resource type prefix (e.g. ``"repo"``, ``"blob"``).
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
        # Reject unknown keys
        for key in syntax.keys():
            if key not in self.schema_keys:
                return None

        result: t.Dict[str, t.Any] = {}

        for key, defn in self.schema.items():
            if defn.multiple:
                param = syntax.get_multi(key)
            else:
                param = syntax.get_single(key)

            if param is not None:
                # Named parameter present
                if key == self.positional_name and syntax.positional is not None:
                    # Positional cannot coexist with named
                    return None

                if defn.multiple:
                    values = param if isinstance(param, list) else [param]
                    if not values:
                        return None
                    if not all(defn.validate(v) for v in values):
                        return None
                    result[key] = values
                else:
                    if not defn.validate(param):
                        return None
                    result[key] = param
            elif key == self.positional_name and syntax.positional is not None:
                # Use positional value
                positional = syntax.positional
                if not defn.validate(positional):
                    return None
                result[key] = [positional] if defn.multiple else positional
            elif defn.required:
                return None
            else:
                result[key] = defn.default

        return result

    def format(self, values: t.Dict[str, t.Any]) -> str:
        """Format validated values back into a canonical scope string."""
        params: t.List[t.Tuple[str, str]] = []
        positional: t.Optional[str] = None

        for key in self.schema:
            value = values.get(key)
            if value is None:
                continue

            defn = self.schema[key]

            # Normalize
            normalized = defn.normalize(value) if defn.normalize else value

            # Skip default values
            if not defn.required and defn.default is not None:
                if defn.multiple:
                    if _array_param_equals(defn.default, normalized):
                        continue
                elif normalized == defn.default:
                    continue

            if isinstance(normalized, (list, tuple)):
                if key == self.positional_name and len(normalized) == 1:
                    positional = str(normalized[0])
                else:
                    # Deduplicate preserving order
                    seen: t.Set[str] = set()
                    for v in normalized:
                        s = str(v)
                        if s not in seen:
                            seen.add(s)
                            params.append((key, s))
            else:
                if key == self.positional_name:
                    positional = str(normalized)
                else:
                    params.append((key, str(normalized)))

        syntax = ScopeStringSyntax(
            prefix=self.prefix,
            positional=positional,
            params=_pairs_to_dict(params) if params else {},
        )
        return str(syntax)

    def format_values(self, values: t.Dict[str, t.Any]) -> str:
        """Alias for format() for API compatibility."""
        return self.format(values)


def _array_param_equals(a: t.Sequence[t.Any], b: t.Sequence[t.Any]) -> bool:
    """Check if two param arrays contain the same elements (order-independent)."""
    if len(a) != len(b):
        return False
    a_set = set(str(x) for x in a)
    b_set = set(str(x) for x in b)
    return a_set == b_set


def _pairs_to_dict(pairs: t.List[t.Tuple[str, str]]) -> t.Dict[str, t.List[str]]:
    """Convert a list of key-value pairs into a multi-value dict."""
    result: t.Dict[str, t.List[str]] = {}
    for key, val in pairs:
        result.setdefault(key, []).append(val)
    return result

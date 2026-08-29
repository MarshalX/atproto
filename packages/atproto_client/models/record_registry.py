import importlib
import typing as t

if t.TYPE_CHECKING:
    from atproto_client.models.unknown_type import UnknownRecordType

#: NSID to either a resolved record class or the (models package, alias) pair it is imported from.
_REGISTRY: t.Dict[str, t.Union[t.Type['UnknownRecordType'], t.Tuple[str, str]]] = {}


def register_record_types(models_package: str, aliases: t.Mapping[str, str]) -> None:
    """Register the record models a generated package defines.

    Registration is by name, so no model module is imported until a record of that type is
    actually decoded.

    Args:
        models_package: Import path of the generated models package.
        aliases: NSID to the alias of the module holding its ``Record``.
    """
    for nsid, alias in aliases.items():
        _REGISTRY[nsid] = (models_package, alias)


def resolve_record_type(nsid: str) -> t.Optional[t.Type['UnknownRecordType']]:
    """Return the record model registered for an NSID, or :obj:`None` if there is none."""
    entry = _REGISTRY.get(nsid)
    if entry is None:
        return None

    if isinstance(entry, tuple):
        models_package, alias = entry
        entry = getattr(importlib.import_module(models_package), alias).Record
        _REGISTRY[nsid] = entry

    return entry


class _RecordTypeMapping(t.Mapping[str, t.Type['UnknownRecordType']]):
    """Read-only view of the registry. Kept for code that used the generated dict directly."""

    def __getitem__(self, nsid: str) -> t.Type['UnknownRecordType']:
        model = resolve_record_type(nsid)
        if model is None:
            raise KeyError(nsid)

        return model

    def __iter__(self) -> t.Iterator[str]:
        return iter(_REGISTRY)

    def __len__(self) -> int:
        return len(_REGISTRY)


RECORD_TYPE_TO_MODEL_CLASS = _RecordTypeMapping()

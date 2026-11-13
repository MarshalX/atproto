import typing as t

_warnings: t.Dict[str, None] = {}


def warn(message: str) -> None:
    """Record what a run with ``skip_invalid`` left out or weakened. Repeated messages are kept once."""
    _warnings.setdefault(message)


def get_warnings() -> t.List[str]:
    return list(_warnings)


def clear_warnings() -> None:
    _warnings.clear()

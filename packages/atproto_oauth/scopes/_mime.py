"""MIME type and Accept header matching for blob scopes."""

import typing as t


def is_accept(value: str) -> bool:
    """Check if value is a valid accept pattern (``*/*``, ``image/*``, ``image/png``)."""
    if value == '*/*':
        return True
    if not _is_string_slash_string(value):
        return False
    return '*' not in value or value.endswith('/*')


def is_mime(value: str) -> bool:
    """Check if value is a concrete MIME type (no wildcards)."""
    return _is_string_slash_string(value) and '*' not in value


def matches_accept(accept: str, mime: str) -> bool:
    """Check if a MIME type matches an accept pattern."""
    if not is_mime(mime):
        return False
    return _matches_accept_unsafe(accept, mime)


def matches_any_accept(patterns: t.Iterable[str], mime: str) -> bool:
    """Check if a MIME type matches any of the accept patterns."""
    if not is_mime(mime):
        return False
    for accept in patterns:
        if _matches_accept_unsafe(accept, mime):
            return True
    return False


def _is_string_slash_string(value: str) -> bool:
    """Check if value has exactly one slash with non-empty parts on both sides."""
    slash_idx = value.find('/')
    if slash_idx == -1:
        return False
    if slash_idx == 0:
        return False
    if slash_idx == len(value) - 1:
        return False
    if '/' in value[slash_idx + 1 :]:
        return False
    if ' ' in value:
        return False
    return True


def _matches_accept_unsafe(accept: str, mime: str) -> bool:
    """Match without re-validating mime."""
    if accept == '*/*':
        return True
    if accept.endswith('/*'):
        return mime.startswith(accept[:-1])
    return accept == mime

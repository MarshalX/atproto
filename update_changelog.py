#!/usr/bin/env python3
"""Prepend a new release section to CHANGES.md from a GitHub release. Used in CI/CD."""

import datetime as dt
import os
import sys
import traceback
from pathlib import Path

import httpx

_CHANGES_PATH = Path(__file__).parent.joinpath('CHANGES.md').absolute()

_GITHUB_API_BASE_URL = 'https://api.github.com'
_DEFAULT_REPO = 'MarshalX/atproto'

_TOP_HEADING = '# Change Log'

_DROP_HEADING = "## What's Changed"
_FOOTER_MARKERS = ('**Full Changelog**', '## New Contributors')


def _emit_github_error(message: str, title: str = 'update_changelog.py failed') -> None:
    """Surface a failure as a GitHub Actions error annotation (no-op outside CI)."""
    if 'CI' not in os.environ:
        return

    # Escape per the GitHub workflow-command spec so multi-line tracebacks render.
    escaped = message.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::error title={title}::{escaped}')  # noqa: T201


def _set_output(name: str, value: str) -> None:
    """Expose a value to later workflow steps via $GITHUB_OUTPUT."""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if not github_output:
        return

    with open(github_output, 'a', encoding='UTF-8') as f:
        f.write(f'{name}={value}\n')


def _print(*args) -> None:
    if 'CI' in os.environ:
        print(*args, file=sys.stderr)  # noqa: T201
        return

    print(*args)  # noqa: T201


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f'Missing required environment variable: {name}')

    return value


def _normalize_version(tag: str) -> str:
    return tag[1:] if tag.startswith('v') else tag


def _format_date(published_at: str) -> str:
    parsed = dt.datetime.fromisoformat(published_at.replace('Z', '+00:00'))
    return parsed.strftime('%d.%m.%Y')


def _fetch_release(tag: str) -> dict:
    """Fetch a release from the GitHub API. Empty ``tag`` resolves to the latest release.

    Used by the manual (workflow_dispatch) path, where there is no release event payload.
    """
    repo = os.environ.get('GITHUB_REPOSITORY') or _DEFAULT_REPO
    if tag:
        url = f'{_GITHUB_API_BASE_URL}/repos/{repo}/releases/tags/{tag}'
    else:
        url = f'{_GITHUB_API_BASE_URL}/repos/{repo}/releases/latest'

    headers = {'Accept': 'application/vnd.github+json'}
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'

    _print(f'- Fetching release from {url} ...')
    response = httpx.get(url, headers=headers, follow_redirects=True)
    response.raise_for_status()
    return response.json()


def _clean_body(body: str) -> str:
    """Strip GitHub's auto-notes scaffolding (``## What's Changed`` header and footer)."""
    lines = body.replace('\r\n', '\n').split('\n')

    # Cut the footer and everything after it
    for idx, line in enumerate(lines):
        if any(line.strip().startswith(marker) for marker in _FOOTER_MARKERS):
            lines = lines[:idx]
            break

    # Drop the leading heading
    lines = [line for line in lines if line.strip() != _DROP_HEADING]

    return '\n'.join(lines).strip()


def _build_section(version: str, date: str, body: str) -> str:
    return f'## Version {version}\n\n**{date}**\n\n{body}\n'


def _insert_section(changes: str, section: str) -> str:
    """Insert the new section right after the top-level heading, before the latest version."""
    heading = f'{_TOP_HEADING}\n'
    if not changes.startswith(heading):
        raise RuntimeError(f'CHANGES.md does not start with the expected {_TOP_HEADING!r} heading')

    rest = changes[len(heading) :].lstrip('\n')
    return f'{heading}\n{section}\n{rest}'


def _replace_section(changes: str, version: str, section: str) -> str:
    """Replace an existing ``## Version X.Y.Z`` block in place (used by --force / past releases)."""
    marker = f'## Version {version}\n'
    start = changes.find(marker)
    if start == -1:
        raise RuntimeError(f'Version {version} not found in CHANGES.md')

    # The next version heading marks the end of this block; -1 means it is the last block.
    next_heading = changes.find('\n## Version ', start + len(marker))
    end = len(changes) if next_heading == -1 else next_heading + 1

    suffix = changes[end:]
    # Separate from the following section with a blank line; nothing extra at EOF.
    joiner = '\n' if suffix else ''
    return f'{changes[:start]}{section}{joiner}{suffix}'


def main() -> None:
    """Prepend a release section to CHANGES.md from the release payload. Used in CI/CD."""
    # The release event provides the payload directly via env; manual dispatch only knows the
    # tag (or nothing -> latest), so we fetch the release from the API. RELEASE_DATE is the
    # discriminator: it is always present on a release event, never on a manual dispatch.
    if os.environ.get('RELEASE_DATE'):
        tag = _require_env('RELEASE_TAG')
        published_at = os.environ['RELEASE_DATE']
        body = os.environ.get('RELEASE_BODY', '')
    else:
        release = _fetch_release(os.environ.get('RELEASE_TAG', ''))
        tag = release['tag_name']
        published_at = release['published_at']
        body = release.get('body') or ''

    version = _normalize_version(tag)
    date = _format_date(published_at)
    body = _clean_body(body)

    force = os.environ.get('FORCE', '').strip().lower() in ('true', '1', 'yes')

    changes = _CHANGES_PATH.read_text(encoding='UTF-8')
    section = _build_section(version, date, body)

    if f'## Version {version}\n' in changes:
        if not force:
            _print(f'- CHANGES.md already contains version {version}; nothing to do (set force to overwrite).')
            _set_output('changed', 'false')
            return
        _CHANGES_PATH.write_text(_replace_section(changes, version, section), encoding='UTF-8')
        _print(f'- Replaced CHANGES.md section for version {version} (force).')
    else:
        _CHANGES_PATH.write_text(_insert_section(changes, section), encoding='UTF-8')
        _print(f'- Added CHANGES.md section for version {version}.')

    commit_message = f'Update changelog for v{version}'
    _set_output('changed', 'true')
    _set_output('version', version)
    _set_output('commit_message', commit_message)
    print(commit_message)  # noqa: T201


if __name__ == '__main__':
    try:
        main()
    except Exception:
        _emit_github_error(traceback.format_exc())
        raise

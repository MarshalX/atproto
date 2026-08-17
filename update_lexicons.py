#!/usr/bin/env python3
"""Fetch new lexicons and regenerate code and docs. Used in CI/CD."""

import os
import subprocess
import sys
import traceback
import typing as t
import zipfile
from io import BytesIO
from pathlib import Path

import httpx
from pydantic_core import from_json

_GITHUB_BASE_URL = 'https://github.com'
_GITHUB_API_BASE_URL = 'https://api.github.com'

_ORG_NAME = 'bluesky-social'
_DEFAULT_BRANCH_NAME = 'main'

_LEXICONS_FOLDER_NAME = 'lexicons'


class LexiconSource(t.NamedTuple):
    """Upstream repository to fetch lexicons from."""

    repo: str
    branch: str = _DEFAULT_BRANCH_NAME
    subpath: str = ''  #: Restricts the fetch to a subtree of the repo's lexicons dir.
    org: str = _ORG_NAME


_SOURCES = (
    LexiconSource(repo='atproto'),
    LexiconSource(repo='jetstream', subpath='network/'),
)

_MANDATORY_REQUEST_HEADERS = {'Content-Type-': 'application/json'}

_FOLDER_TO_WRITE_LEXICONS = Path(__file__).parent.joinpath('lexicons').absolute()

_FOLDER_OF_GEN_DOCS = Path(__file__).parent.joinpath('docs', 'source', 'atproto').absolute()

_FOLDER_OF_MODELS = Path(__file__).parent.joinpath('packages', 'atproto_client', 'models').absolute()


def _build_last_commit_api_url(source: LexiconSource) -> str:
    return f'{_GITHUB_API_BASE_URL}/repos/{source.org}/{source.repo}/commits'


def _build_src_download_url(source: LexiconSource) -> str:
    return f'{_GITHUB_BASE_URL}/{source.org}/{source.repo}/archive/refs/heads/{source.branch}.zip'


def _get_last_commit_info(source: LexiconSource) -> t.Tuple[str, str, str]:
    response = httpx.get(
        url=_build_last_commit_api_url(source),
        params={
            'path': f'{_LEXICONS_FOLDER_NAME}/{source.subpath}'.rstrip('/'),
            'sha': source.branch,
            'per_page': 1,
        },
        headers=_MANDATORY_REQUEST_HEADERS,
        timeout=5,
    )
    response.raise_for_status()

    response_json = from_json(response.content)
    commit_info = response_json[0]

    sha = commit_info['sha']
    commit_date = commit_info['commit']['author']['date']
    message = commit_info['commit']['message']

    return sha, commit_date, message


def _download_zip_with_code(source: LexiconSource) -> BytesIO:
    response = httpx.get(_build_src_download_url(source), follow_redirects=True)
    response.raise_for_status()

    zip_file_bytes = BytesIO()
    zip_file_bytes.write(response.content)

    return zip_file_bytes


def _build_valid_path_to_lexicons(source: LexiconSource) -> str:
    return f'{source.repo}-{source.branch}/{_LEXICONS_FOLDER_NAME}/'


def _validate_lexicon_path_prefix(path: str, source: LexiconSource) -> bool:
    return path.startswith(f'{_build_valid_path_to_lexicons(source)}{source.subpath}')


ExtractedFiles = t.Dict[str, bytes]


def _extract_zip(zip_file: BytesIO, source: LexiconSource) -> ExtractedFiles:
    """Extract lexicons of the source keyed by their flattened output filename."""
    archive = zipfile.ZipFile(zip_file)

    extracted_files: ExtractedFiles = {}
    for name in archive.namelist():
        if not _validate_lexicon_path_prefix(name, source):
            continue

        content = archive.read(name)
        if not content:
            # if dir name
            continue

        extracted_files[_format_lexicon_filename(name, source)] = content

    return extracted_files


def _merge_extracted_lexicons(sources_files: t.List[t.Tuple[LexiconSource, ExtractedFiles]]) -> ExtractedFiles:
    """Merge lexicons of all sources, rejecting any filename claimed by more than one."""
    merged: ExtractedFiles = {}
    owner_by_filename: t.Dict[str, str] = {}

    for source, files in sources_files:
        for filename, content in files.items():
            owner = owner_by_filename.get(filename)
            if owner is not None:
                raise RuntimeError(f'Lexicon {filename} is provided by both {owner} and {source.repo}')

            owner_by_filename[filename] = source.repo
            merged[filename] = content

    return merged


def _get_path_to_write_lexicon(filename: str) -> Path:
    return _FOLDER_TO_WRITE_LEXICONS.joinpath(filename)


def _write_to_file(filename: str, content: bytes) -> None:
    path_to_write = _get_path_to_write_lexicon(filename)
    with open(path_to_write, 'w', encoding='UTF-8') as f:
        f.write(content.decode('UTF-8'))


def _format_lexicon_filename(original_filename: str, source: LexiconSource) -> str:
    filename = original_filename.replace(_build_valid_path_to_lexicons(source), '')
    return filename.replace('/', '.')


def _write_extracted_lexicons(extracted_files: ExtractedFiles) -> None:
    for filename, content in extracted_files.items():
        _write_to_file(filename, content)


def _remove_content_in_path(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            _remove_content_in_path(child)
            if child.exists():
                child.rmdir()
        else:
            child.unlink()


def _emit_github_error(message: str, title: str = 'update_lexicons.py failed') -> None:
    """Surface a failure as a GitHub Actions error annotation (no-op outside CI)."""
    if 'CI' not in os.environ:
        return

    # Escape per the GitHub workflow-command spec so multi-line tracebacks render.
    escaped = message.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::error title={title}::{escaped}')  # noqa: T201


def _set_commit_message_output(commit_message: str) -> None:
    """Expose the commit message to later workflow steps via $GITHUB_OUTPUT."""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if not github_output:
        return

    with open(github_output, 'a', encoding='UTF-8') as f:
        f.write(f'commit_message={commit_message}\n')


def _run_subprocess(command: t.List[str]) -> None:
    # check=False: the return code is reported to GitHub below instead of raising
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True, check=False)  # noqa: S603
    if result.stderr:
        sys.stderr.write(result.stderr)
    if result.returncode != 0:
        _emit_github_error(f'`{" ".join(command)}` exited with {result.returncode}\n{result.stderr}')
        sys.exit(result.returncode)


def _print(*args) -> None:
    if 'CI' in os.environ:
        print(*args, file=sys.stderr)  # noqa: T201
        return

    print(*args)  # noqa: T201


def main() -> None:
    """Fetch new lexicons and regenerate code and docs. Used in CI/CD."""
    sources_files = []
    revisions = []
    for source in _SOURCES:
        _print(f'- Fetching lexicons from the latest commit of {source.repo}...')
        sha, commit_date, _ = _get_last_commit_info(source)
        revisions.append(f'{source.repo}@{sha[:7]} ({commit_date})')
        sources_files.append((source, _extract_zip(_download_zip_with_code(source), source)))

    _remove_content_in_path(_FOLDER_TO_WRITE_LEXICONS)
    _write_extracted_lexicons(_merge_extracted_lexicons(sources_files))

    # remove all generated models
    for item in os.listdir(_FOLDER_OF_MODELS):
        path = Path(_FOLDER_OF_MODELS, item)
        if path.is_dir():
            _remove_content_in_path(path)
            path.rmdir()
    _print('- Running codegen (poetry run atp -s gen all)...')
    _run_subprocess(['poetry', 'run', 'atp', '-s', 'gen', 'all'])

    _print('- Running ruff (poetry run ruff check --quiet --fix .)...')
    _run_subprocess(['poetry', 'run', 'ruff', 'check', '--quiet', '--fix', '.'])

    _print('- Running ruff format (poetry run ruff --quiet format .)...')
    _run_subprocess(['poetry', 'run', 'ruff', 'format', '--quiet', '.'])

    _print('- Generating docs (make -s -C docs gen)...')
    _remove_content_in_path(_FOLDER_OF_GEN_DOCS)
    _run_subprocess(['make', '-s', '-C', 'docs', 'gen'])

    commit_message = f'Update lexicons fetched from {", ".join(revisions)}'
    _print(f'Commit message: {commit_message}')

    _set_commit_message_output(commit_message)
    print(commit_message)  # noqa: T201


if __name__ == '__main__':
    try:
        main()
    except Exception:
        _emit_github_error(traceback.format_exc())
        raise

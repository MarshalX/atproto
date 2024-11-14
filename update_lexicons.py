#!/usr/bin/env python3
"""Fetch new lexicons and regenerate code and docs. Used in CI/CD."""

import os
import subprocess
import typing as t
import zipfile
from io import BytesIO
from pathlib import Path

import httpx
from pydantic_core import from_json

_GITHUB_BASE_URL = 'https://github.com'
_GITHUB_API_BASE_URL = 'https://api.github.com'

_ORG_NAME = 'bluesky-social'
_REPO_NAME = 'atproto'
_DEFAULT_BRANCH_NAME = 'main'

_LEXICONS_FOLDER_NAME = 'lexicons'

_MANDATORY_REQUEST_HEADERS = {'Content-Type-': 'application/json'}

_FOLDER_TO_WRITE_LEXICONS = Path(__file__).parent.joinpath('lexicons').absolute()

_FOLDER_OF_GEN_DOCS = Path(__file__).parent.joinpath('docs', 'source', 'atproto').absolute()

_FOLDER_OF_MODELS = Path(__file__).parent.joinpath('packages', 'atproto_client', 'models').absolute()


def _build_last_commit_api_url() -> str:
    return f'{_GITHUB_API_BASE_URL}/repos/{_ORG_NAME}/{_REPO_NAME}/commits'


def _build_src_download_url() -> str:
    return f'{_GITHUB_BASE_URL}/{_ORG_NAME}/{_REPO_NAME}/archive/refs/heads/{_DEFAULT_BRANCH_NAME}.zip'


def _get_last_commit_info() -> t.Tuple[str, str, str]:
    response = httpx.get(
        url=_build_last_commit_api_url(),
        params={'path': _LEXICONS_FOLDER_NAME, 'sha': _DEFAULT_BRANCH_NAME, 'per_page': 1},
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


def _download_zip_with_code() -> BytesIO:
    response = httpx.get(_build_src_download_url(), follow_redirects=True)
    response.raise_for_status()

    zip_file_bytes = BytesIO()
    zip_file_bytes.write(response.content)

    return zip_file_bytes


def _build_valid_path_to_lexicons() -> str:
    return f'{_REPO_NAME}-{_DEFAULT_BRANCH_NAME}/{_LEXICONS_FOLDER_NAME}/'


def _validate_lexicon_path_prefix(path: str) -> bool:
    return path.startswith(_build_valid_path_to_lexicons())


ExtractedFiles = t.Dict[str, bytes]


def _extract_zip(zip_file: BytesIO) -> ExtractedFiles:
    archive = zipfile.ZipFile(zip_file)

    extracted_files: ExtractedFiles = {}
    for name in archive.namelist():
        if _validate_lexicon_path_prefix(name):
            extracted_files[name] = archive.read(name)

    return extracted_files


def _get_path_to_write_lexicon(filename: str) -> Path:
    return _FOLDER_TO_WRITE_LEXICONS.joinpath(filename)


def _write_to_file(filename: str, content: bytes) -> None:
    path_to_write = _get_path_to_write_lexicon(filename)
    with open(path_to_write, 'w', encoding='UTF-8') as f:
        f.write(content.decode('UTF-8'))


def _format_lexicon_filename(original_filename: str) -> str:
    filename = original_filename.replace(_build_valid_path_to_lexicons(), '')
    return filename.replace('/', '.')


def _write_extracted_lexicons(extracted_files: ExtractedFiles) -> None:
    for filename, content in extracted_files.items():
        if not content:
            # if dir name
            continue

        _write_to_file(_format_lexicon_filename(filename), content)


def _remove_content_in_path(path: Path) -> None:
    for child in path.iterdir():
        if child.is_dir():
            _remove_content_in_path(child)
            if child.exists():
                child.rmdir()
        else:
            child.unlink()


def _run_subprocess(command: t.List[str]) -> None:
    result = subprocess.run(command)  # noqa: S603
    if result.returncode != 0:
        exit(result.returncode)


def _print(*args) -> None:
    if 'CI' in os.environ:
        return

    print(*args)  # noqa: T201


def main() -> None:
    """Fetch new lexicons and regenerate code and docs. Used in CI/CD."""
    _print('- Fetching lexicons from the latest commit...')
    sha, commit_date, _ = _get_last_commit_info()

    _remove_content_in_path(_FOLDER_TO_WRITE_LEXICONS)
    _write_extracted_lexicons(_extract_zip(_download_zip_with_code()))

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

    commit_message = f'Update lexicons fetched from {sha[:7]} committed {commit_date}'
    _print(f'Commit message: {commit_message}')

    print(commit_message)  # noqa: T201


if __name__ == '__main__':
    main()

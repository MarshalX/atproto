import typing as t
import zipfile
from io import BytesIO
from pathlib import Path

import httpx

_GITHUB_BASE_URL = 'https://github.com'
_GITHUB_API_BASE_URL = 'https://api.github.com'

_ORG_NAME = 'bluesky-social'
_REPO_NAME = 'atproto'
_DEFAULT_BRANCH_NAME = 'main'

_LEXICONS_FOLDER_NAME = 'lexicons'

_MANDATORY_REQUEST_HEADERS = {'Content-Type-': 'application/json'}

_FOLDER_TO_WRITE_LEXICONS = Path(__file__).parent.joinpath('lexicons').absolute()


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

    response_json = response.json()
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
    filename = filename.replace('/', '.')
    return filename


def _write_extracted_lexicons(extracted_files: ExtractedFiles) -> None:
    for filename, content in extracted_files.items():
        if not content:
            # if dir name
            continue

        _write_to_file(_format_lexicon_filename(filename), content)


def main():
    sha, commit_date, _ = _get_last_commit_info()

    print('Successfully fetch lexicons! Next steps:')

    print('- Run codegen (poetry run atp gen all)')

    print('- Run ruff (poetry run ruff .)')
    print('- Run black (poetry run black .)')

    print('- Gen docs (cd docs && make gen)')

    print('- Add all new files to Git (git add)')
    print('- Commit with the message below:', end='\n\n')

    print(f'Update lexicons fetched from {sha[:7]} committed {commit_date}')
    _write_extracted_lexicons(_extract_zip(_download_zip_with_code()))


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Fetch new lexicons and regenerate code and docs. Used in CI/CD."""

import json
import os
import subprocess
import sys
import traceback
import typing as t
import uuid
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
_LEXICON_FILE_SUFFIX = '.json'

_DESCRIPTION_KEY = 'description'
_PERMISSIONS_KEY = 'permissions'

_SOURCE_TRAILER = 'Lexicon-Source'

_TITLE_MAX_LENGTH = 72
#: Namespaces most SDK users care about, most notable first. Steers which addition headlines the title.
_NAMESPACE_PRIORITY = ('app.bsky', 'com.atproto', 'network.bsky', 'chat.bsky')
#: Moderation and Bluesky-internal namespaces. Vendored and generated, but not what SDK users track.
_SECONDARY_NAMESPACES = ('tools.ozone', 'internal.')
_SECONDARY_LABEL = 'tools.ozone and internal namespaces'

_BODY_SECTION_LIMIT = 25
_BODY_VALUE_MAX_LENGTH = 60


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


class SourceRevision(t.NamedTuple):
    """Upstream commit a source's lexicons were fetched from."""

    source: LexiconSource
    sha: str
    date: str


_MANDATORY_REQUEST_HEADERS = {'Content-Type-': 'application/json'}

_FOLDER_TO_WRITE_LEXICONS = Path(__file__).parent.joinpath('lexicons').absolute()

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


ParsedLexicons = t.Dict[str, t.Dict[str, t.Any]]
LexiconLeaves = t.Dict[str, t.Any]

#: Marks the absent side of a constraint that was only added or only removed.
_MISSING = object()


class ConstraintChange(t.NamedTuple):
    """A leaf value of a surviving field that was added, removed, or modified."""

    path: str
    old: t.Any
    new: t.Any


class LexiconChange(t.NamedTuple):
    """Semantic changes within a single lexicon."""

    added_defs: t.List[str]
    removed_defs: t.List[str]
    added_fields: t.List[str]
    removed_fields: t.List[str]
    constraints: t.List[ConstraintChange]
    permission_set: bool


class LexiconDiff(t.NamedTuple):
    """Semantic difference between two snapshots of the lexicons dir."""

    added_lexicons: t.List[str]
    removed_lexicons: t.List[str]
    added_defs: t.List[str]
    removed_defs: t.List[str]
    added_fields: t.List[str]
    removed_fields: t.List[str]
    constraints: t.List[ConstraintChange]
    permission_sets: t.List[str]
    description_only: t.List[str]
    changed_lexicons: t.List[str]


def _read_lexicons_on_disk() -> ParsedLexicons:
    """Parse the lexicons currently vendored in the lexicons dir, keyed by NSID."""
    lexicons: ParsedLexicons = {}
    for path in _FOLDER_TO_WRITE_LEXICONS.iterdir():
        if path.suffix != _LEXICON_FILE_SUFFIX:
            continue

        lexicons[path.stem] = from_json(path.read_bytes())

    return lexicons


def _parse_extracted_lexicons(extracted_files: ExtractedFiles) -> ParsedLexicons:
    """Parse the merged lexicons keyed by NSID, matching the on-disk layout."""
    return {
        filename[: -len(_LEXICON_FILE_SUFFIX)]: from_json(content)
        for filename, content in extracted_files.items()
        if filename.endswith(_LEXICON_FILE_SUFFIX)
    }


def _flatten(node: t.Any, prefix: str = '') -> LexiconLeaves:
    """Flatten a lexicon subtree into dotted paths, dropping human-facing descriptions."""
    if not isinstance(node, dict):
        return {prefix: node}

    leaves: LexiconLeaves = {}
    for key, value in node.items():
        if key == _DESCRIPTION_KEY:
            continue

        leaves.update(_flatten(value, f'{prefix}.{key}' if prefix else key))

    return leaves


def _flatten_defs(lexicon: t.Dict[str, t.Any]) -> t.Dict[str, LexiconLeaves]:
    return {name: _flatten(body) for name, body in lexicon.get('defs', {}).items()}


def _ancestor_paths(paths: t.Iterable[str]) -> t.Set[str]:
    """Collect every intermediate path along the given leaf paths."""
    ancestors = set()
    for path in paths:
        parts = path.split('.')
        for depth in range(1, len(parts)):
            ancestors.add('.'.join(parts[:depth]))

    return ancestors


def _collapse_nested(paths: t.Iterable[str]) -> t.List[str]:
    """Drop paths already covered by a shallower path in the same set."""
    unique = sorted(set(paths))
    return [path for path in unique if not any(path.startswith(f'{other}.') for other in unique)]


def _is_permissions_path(path: str) -> bool:
    return path == _PERMISSIONS_KEY or path.endswith(f'.{_PERMISSIONS_KEY}')


def _diff_def(qualified_name: str, old_leaves: LexiconLeaves, new_leaves: LexiconLeaves) -> LexiconChange:
    """Split the leaf changes of one def into new fields, removed fields, and constraint changes.

    A leaf whose parent path is unknown to the other side is a whole new (or gone) field; anything
    else only tightens or loosens an existing one.
    """
    old_ancestors = _ancestor_paths(old_leaves)
    new_ancestors = _ancestor_paths(new_leaves)

    added_field_paths: t.List[str] = []
    removed_field_paths: t.List[str] = []
    constraints: t.List[ConstraintChange] = []
    permission_set = False

    for path in sorted(set(new_leaves) - set(old_leaves)):
        parent = path.rpartition('.')[0]
        if parent and parent not in old_ancestors:
            added_field_paths.append(parent)
        else:
            constraints.append(ConstraintChange(f'{qualified_name}.{path}', _MISSING, new_leaves[path]))

    for path in sorted(set(old_leaves) - set(new_leaves)):
        parent = path.rpartition('.')[0]
        if parent and parent not in new_ancestors:
            removed_field_paths.append(parent)
        else:
            constraints.append(ConstraintChange(f'{qualified_name}.{path}', old_leaves[path], _MISSING))

    for path in sorted(set(old_leaves) & set(new_leaves)):
        if old_leaves[path] == new_leaves[path]:
            continue

        if _is_permissions_path(path):
            # Permission sets list every lxm in the app, so they churn on any unrelated addition.
            permission_set = True
        else:
            constraints.append(ConstraintChange(f'{qualified_name}.{path}', old_leaves[path], new_leaves[path]))

    return LexiconChange(
        added_defs=[],
        removed_defs=[],
        added_fields=[f'{qualified_name}.{path}' for path in _collapse_nested(added_field_paths)],
        removed_fields=[f'{qualified_name}.{path}' for path in _collapse_nested(removed_field_paths)],
        constraints=constraints,
        permission_set=permission_set,
    )


def _diff_lexicon(nsid: str, old_lexicon: t.Dict[str, t.Any], new_lexicon: t.Dict[str, t.Any]) -> LexiconChange:
    """Compare two versions of one lexicon at def and field level."""
    old_defs = _flatten_defs(old_lexicon)
    new_defs = _flatten_defs(new_lexicon)

    added_fields: t.List[str] = []
    removed_fields: t.List[str] = []
    constraints: t.List[ConstraintChange] = []
    permission_set = False

    for name in sorted(set(old_defs) & set(new_defs)):
        change = _diff_def(f'{nsid}#{name}', old_defs[name], new_defs[name])
        added_fields.extend(change.added_fields)
        removed_fields.extend(change.removed_fields)
        constraints.extend(change.constraints)
        permission_set = permission_set or change.permission_set

    return LexiconChange(
        added_defs=[f'{nsid}#{name}' for name in sorted(set(new_defs) - set(old_defs))],
        removed_defs=[f'{nsid}#{name}' for name in sorted(set(old_defs) - set(new_defs))],
        added_fields=added_fields,
        removed_fields=removed_fields,
        constraints=constraints,
        permission_set=permission_set,
    )


def _is_empty_change(change: LexiconChange) -> bool:
    return not any(
        (
            change.added_defs,
            change.removed_defs,
            change.added_fields,
            change.removed_fields,
            change.constraints,
            change.permission_set,
        )
    )


def _diff_lexicons(old: ParsedLexicons, new: ParsedLexicons) -> LexiconDiff:
    """Diff two snapshots of the lexicons dir, keeping description-only churn out of the way."""
    added_defs: t.List[str] = []
    removed_defs: t.List[str] = []
    added_fields: t.List[str] = []
    removed_fields: t.List[str] = []
    constraints: t.List[ConstraintChange] = []
    permission_sets: t.List[str] = []
    description_only: t.List[str] = []
    changed_lexicons: t.List[str] = []

    for nsid in sorted(set(old) & set(new)):
        if old[nsid] == new[nsid]:
            continue

        change = _diff_lexicon(nsid, old[nsid], new[nsid])
        if _is_empty_change(change):
            description_only.append(nsid)
            continue

        changed_lexicons.append(nsid)
        added_defs.extend(change.added_defs)
        removed_defs.extend(change.removed_defs)
        added_fields.extend(change.added_fields)
        removed_fields.extend(change.removed_fields)
        constraints.extend(change.constraints)
        if change.permission_set:
            permission_sets.append(nsid)

    return LexiconDiff(
        added_lexicons=sorted(set(new) - set(old)),
        removed_lexicons=sorted(set(old) - set(new)),
        added_defs=added_defs,
        removed_defs=removed_defs,
        added_fields=added_fields,
        removed_fields=removed_fields,
        constraints=constraints,
        permission_sets=permission_sets,
        description_only=description_only,
        changed_lexicons=changed_lexicons,
    )


def _has_semantic_changes(diff: LexiconDiff) -> bool:
    return bool(diff.added_lexicons or diff.removed_lexicons or diff.changed_lexicons)


def _is_secondary(name: str) -> bool:
    return name.startswith(_SECONDARY_NAMESPACES)


def _partition_diff(diff: LexiconDiff) -> t.Tuple[LexiconDiff, LexiconDiff]:
    """Split a diff into the namespaces SDK users track and the ones they rarely touch.

    Ozone churns on nearly every upstream commit, so letting it headline the title or inflate the
    changed count buries the changes that matter.
    """

    def take(names: t.List[str], secondary: bool) -> t.List[str]:
        return [name for name in names if _is_secondary(name) == secondary]

    def build(secondary: bool) -> LexiconDiff:
        return LexiconDiff(
            added_lexicons=take(diff.added_lexicons, secondary),
            removed_lexicons=take(diff.removed_lexicons, secondary),
            added_defs=take(diff.added_defs, secondary),
            removed_defs=take(diff.removed_defs, secondary),
            added_fields=take(diff.added_fields, secondary),
            removed_fields=take(diff.removed_fields, secondary),
            constraints=[change for change in diff.constraints if _is_secondary(change.path) == secondary],
            permission_sets=take(diff.permission_sets, secondary),
            description_only=take(diff.description_only, secondary),
            changed_lexicons=take(diff.changed_lexicons, secondary),
        )

    return build(secondary=False), build(secondary=True)


_PATH_SHORTENINGS = (
    ('.properties.', '.'),
    ('.parameters.', '.'),
    ('.input.schema.', '.input.'),
    ('.output.schema.', '.output.'),
    ('.items.', '[].'),
    ('#main.', '.'),
)


def _short_path(path: str) -> str:
    """Trim structural lexicon keys so a path reads like the API surface it describes."""
    for structural, readable in _PATH_SHORTENINGS:
        path = path.replace(structural, readable)

    return path


def _namespace_rank(namespace: str) -> int:
    for rank, prefix in enumerate(_NAMESPACE_PRIORITY):
        if namespace.startswith(prefix):
            return rank

    return len(_NAMESPACE_PRIORITY)


def _group_by_namespace(nsids: t.List[str]) -> t.List[str]:
    """Collapse sibling NSIDs into ``namespace.*``, most notable namespace first."""
    by_namespace: t.Dict[str, t.List[str]] = {}
    for nsid in nsids:
        by_namespace.setdefault(nsid.rpartition('.')[0], []).append(nsid)

    ordered = sorted(by_namespace.items(), key=lambda item: (_namespace_rank(item[0]), -len(item[1]), item[0]))

    return [f'{namespace}.*' if len(members) > 1 else members[0] for namespace, members in ordered]


def _title_candidates(diff: LexiconDiff) -> t.Tuple[str, t.List[str], str]:
    """Pick what the title should headline: the most user-visible addition, else a removal."""
    if diff.added_lexicons:
        return 'add', _group_by_namespace(diff.added_lexicons), 'lexicon'
    if diff.added_defs:
        return 'add', [_short_path(name) for name in diff.added_defs], 'def'
    if diff.added_fields:
        return 'add', [_short_path(name) for name in diff.added_fields], 'field'
    if diff.removed_lexicons:
        return 'remove', _group_by_namespace(diff.removed_lexicons), 'lexicon'

    return '', [], ''


def _pluralize(count: int, noun: str) -> str:
    return f'{count} {noun}' if count == 1 else f'{count} {noun}s'


def _build_title(diff: LexiconDiff) -> str:
    """Build a title that names what actually changed, within ``_TITLE_MAX_LENGTH``."""
    primary, secondary = _partition_diff(diff)
    focus = primary if _has_semantic_changes(primary) else secondary

    if not _has_semantic_changes(focus):
        if diff.description_only:
            return f'Update lexicons: descriptions only ({_pluralize(len(diff.description_only), "lexicon")})'

        return 'Update lexicons'

    suffix = f' ({len(focus.changed_lexicons)} changed)' if focus.changed_lexicons else ''

    verb, names, noun = _title_candidates(focus)
    if not names:
        return f'Update lexicons{suffix}'

    for shown in range(len(names), 0, -1):
        rest = len(names) - shown
        head = ', '.join(names[:shown]) + (f' +{rest} more' if rest else '')
        title = f'Update lexicons: {verb} {head}{suffix}'
        if len(title) <= _TITLE_MAX_LENGTH:
            return title

    if len(names) == 1:
        # One name over budget still says more than a bare count does.
        return f'Update lexicons: {verb} {names[0]}{suffix}'

    return f'Update lexicons: {verb} {_pluralize(len(names), noun)}{suffix}'


def _build_commit_message(title: str, revisions: t.List[SourceRevision]) -> str:
    """Build the commit message: the title plus one machine-readable trailer per source."""
    trailers = [
        f'{_SOURCE_TRAILER}: {revision.source.org}/{revision.source.repo}@{revision.sha} {revision.date}'
        for revision in revisions
    ]

    return '\n'.join([title, '', *trailers])


def _format_value(value: t.Any) -> str:
    text = json.dumps(value, sort_keys=True)
    if len(text) > _BODY_VALUE_MAX_LENGTH:
        text = f'{text[: _BODY_VALUE_MAX_LENGTH - 3]}...'

    return text


def _format_constraint(change: ConstraintChange) -> str:
    path = _short_path(change.path)
    if change.old is _MISSING:
        return f'- `{path}`: added `{_format_value(change.new)}`'
    if change.new is _MISSING:
        return f'- `{path}`: removed'

    return f'- `{path}`: `{_format_value(change.old)}` → `{_format_value(change.new)}`'


def _format_section(heading: str, lines: t.List[str]) -> t.List[str]:
    """Render one PR body section, capping how many entries it lists."""
    if not lines:
        return []

    shown = lines[:_BODY_SECTION_LIMIT]
    rest = len(lines) - len(shown)
    if rest:
        shown = [*shown, f'- ...and {rest} more']

    return [f'### {heading}', '', *shown, '']


def _build_change_sections(diff: LexiconDiff) -> t.List[str]:
    """Render every non-empty section of one diff."""
    lines: t.List[str] = []
    lines += _format_section('New lexicons', [f'- `{nsid}`' for nsid in diff.added_lexicons])
    lines += _format_section('Removed lexicons', [f'- `{nsid}`' for nsid in diff.removed_lexicons])
    lines += _format_section('New defs', [f'- `{_short_path(name)}`' for name in diff.added_defs])
    lines += _format_section('Removed defs', [f'- `{_short_path(name)}`' for name in diff.removed_defs])
    lines += _format_section('New fields', [f'- `{_short_path(name)}`' for name in diff.added_fields])
    lines += _format_section('Removed fields', [f'- `{_short_path(name)}`' for name in diff.removed_fields])
    lines += _format_section('Changed constraints', [_format_constraint(change) for change in diff.constraints])
    lines += _format_section('Updated permission sets', [f'- `{nsid}`' for nsid in diff.permission_sets])
    lines += _format_section('Description-only changes', [f'- `{nsid}`' for nsid in diff.description_only])

    return lines


def _build_body(diff: LexiconDiff, revisions: t.List[SourceRevision]) -> str:
    """Build the PR body: where the lexicons came from and what changed in them."""
    lines = ['Automated update of the vendored lexicons and everything generated from them.', '', 'Fetched from:', '']
    for revision in revisions:
        slug = f'{revision.source.org}/{revision.source.repo}'
        commit_url = f'{_GITHUB_BASE_URL}/{slug}/commit/{revision.sha}'
        lines.append(f'- [`{slug}@{revision.sha[:7]}`]({commit_url}) ({revision.date})')

    lines.append('')

    primary, secondary = _partition_diff(diff)
    primary_sections = _build_change_sections(primary)
    secondary_sections = _build_change_sections(secondary)

    if not primary_sections and not secondary_sections:
        lines.append('No lexicon changes.')
        return '\n'.join(lines)

    if primary_sections:
        lines += ['## Lexicon changes', '', *primary_sections]

    if secondary_sections:
        lines += [
            '<details>',
            f'<summary>Changes in {_SECONDARY_LABEL}</summary>',
            '',
            *secondary_sections,
            '</details>',
        ]

    return '\n'.join(lines).strip()


def _emit_github_error(message: str, title: str = 'update_lexicons.py failed') -> None:
    """Surface a failure as a GitHub Actions error annotation (no-op outside CI)."""
    if 'CI' not in os.environ:
        return

    # Escape per the GitHub workflow-command spec so multi-line tracebacks render.
    escaped = message.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    print(f'::error title={title}::{escaped}')  # noqa: T201


def _set_output(name: str, value: str) -> None:
    """Expose a possibly multi-line value to later workflow steps via $GITHUB_OUTPUT."""
    github_output = os.environ.get('GITHUB_OUTPUT')
    if not github_output:
        return

    delimiter = f'ghadelimiter_{uuid.uuid4()}'
    with open(github_output, 'a', encoding='UTF-8') as f:
        f.write(f'{name}<<{delimiter}\n{value}\n{delimiter}\n')


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
        revisions.append(SourceRevision(source=source, sha=sha, date=commit_date))
        sources_files.append((source, _extract_zip(_download_zip_with_code(source), source)))

    merged_lexicons = _merge_extracted_lexicons(sources_files)

    _print('- Diffing the fetched lexicons against the vendored ones...')
    diff = _diff_lexicons(_read_lexicons_on_disk(), _parse_extracted_lexicons(merged_lexicons))

    _remove_content_in_path(_FOLDER_TO_WRITE_LEXICONS)
    _write_extracted_lexicons(merged_lexicons)

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
    _run_subprocess(['make', '-s', '-C', 'docs', 'gen'])

    title = _build_title(diff)
    body = _build_body(diff, revisions)

    _print(f'Title: {title}')
    _print(body)

    _set_output('title', title)
    _set_output('commit_message', _build_commit_message(title, revisions))
    _set_output('body', body)
    print(title)  # noqa: T201


if __name__ == '__main__':
    try:
        main()
    except Exception:
        _emit_github_error(traceback.format_exc())
        raise

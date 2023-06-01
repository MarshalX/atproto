import re
import subprocess
import typing as t
from pathlib import Path

from atproto.nsid import NSID

_DISCLAIMER_LINES = [
    "# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!",
    '# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.',
    '# This file is part of Python atproto SDK. Licenced under MIT.',
]
_MAX_DISCLAIMER_LEN = max([len(s) for s in _DISCLAIMER_LINES])
DISCLAIMER = '\n'.join(_DISCLAIMER_LINES)
DISCLAIMER = f'{"#" * _MAX_DISCLAIMER_LEN}\n{DISCLAIMER}\n{"#" * _MAX_DISCLAIMER_LEN}\n\n'

PARAMS_MODEL = 'Params'
INPUT_MODEL = 'Data'
OUTPUT_MODEL = 'Response'


def format_code(filepath: Path, quiet: bool = True) -> None:
    if not isinstance(filepath, Path):
        return

    quiet_option = '--quiet'
    if not quiet:
        quiet_option = ''

    # FIXME(MarshalX): doesn't work well with not-project dir
    subprocess.run(['ruff', quiet_option, '--fix', filepath])  # noqa: S603, S607
    subprocess.run(['black', quiet_option, filepath])  # noqa: S603, S607


def append_code(filepath: Path, code: str) -> None:
    _write_code(filepath, code, append=True)


def write_code(filepath: Path, code: str) -> None:
    _write_code(filepath, code)


def _write_code(filepath: Path, code: str, *, append: bool = False) -> None:
    filepath.parent.mkdir(exist_ok=True, parents=True)

    mode = 'w'
    if append:
        mode = 'a'

    with open(filepath, mode=mode, encoding='UTF-8') as f:
        f.write(code)


def get_file_path_parts(nsid: NSID) -> t.List[str]:
    return nsid.segments[:-1] + [f'{convert_camel_case_to_snake_case(nsid.name)}.py']


def get_import_path_old(nsid: NSID) -> str:
    return '.'.join(nsid.segments[:-1] + [f'{convert_camel_case_to_snake_case(nsid.name)}'])


def get_import_path(nsid: NSID) -> str:
    nsid_parts = nsid.segments[:-1] + camel_case_split(nsid.name)
    return ''.join([p.capitalize() for p in nsid_parts])


def convert_camel_case_to_snake_case(string: str) -> str:
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def camel_case_split(string: str) -> t.List[str]:
    # regex by chatgpt
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', string)


def gen_description_by_camel_case_name(name: str) -> str:
    words = camel_case_split(name)
    words = [w.lower() for w in words]
    words[0] = words[0].capitalize()
    return ' '.join(words)


def sort_dict_by_key(d: dict) -> dict:
    return dict(sorted(d.items()))


def get_code_intent(level: int) -> str:
    return ' ' * 4 * level


def join_code(lines: t.List[str]) -> str:
    return '\n'.join(lines)


def get_sync_async_keywords(*, sync: bool) -> t.Tuple[str, str]:
    definition, call = 'async ', 'await '
    if sync:
        definition, call = '', ''

    return definition, call


def capitalize_first_symbol(string: str) -> str:
    if string and string[0].islower():
        chars = list(string[1:])
        chars.insert(0, string[0].upper())
        return ''.join(chars)

    return string

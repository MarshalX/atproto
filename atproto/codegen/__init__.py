import re
import subprocess
from pathlib import Path
from typing import List, Tuple

from atproto.nsid import NSID

DISCLAIMER = [
    '# THIS IS THE AUTO-GENERATED CODE. DON\'T EDIT IT BY HANDS!',
    '# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.',
    '# This file is part of Python atproto SDK. Licenced under MIT.',
]
_MAX_DISCLAIMER_LEN = max([len(s) for s in DISCLAIMER])
DISCLAIMER = '\n'.join(DISCLAIMER)
DISCLAIMER = f'{"#" * _MAX_DISCLAIMER_LEN}\n{DISCLAIMER}\n{"#" * _MAX_DISCLAIMER_LEN}\n\n'

PARAMS_MODEL = 'Params'
INPUT_MODEL = 'Data'
OUTPUT_MODEL = 'Response'


def format_code(filepath: Path) -> None:
    subprocess.run(['black', '--quiet', filepath])
    subprocess.run(['isort', '--quiet', filepath])


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


def get_file_path_parts(nsid: NSID) -> List[str]:
    return nsid.segments[:-1] + [f'{convert_camel_case_to_snake_case(nsid.name)}.py']


def get_import_path_old(nsid: NSID) -> str:
    return '.'.join(nsid.segments[:-1] + [f'{convert_camel_case_to_snake_case(nsid.name)}'])


def get_import_path(nsid: NSID) -> str:
    nsid_parts = nsid.segments[:-1] + camel_case_split(nsid.name)
    alias_name = ''.join([p.capitalize() for p in nsid_parts])
    return alias_name


def convert_camel_case_to_snake_case(string: str) -> str:
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def camel_case_split(string: str):
    # regex by chatgpt
    return re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z]|$)', string)


def gen_description_by_camel_case_name(name: str):
    words = camel_case_split(name)
    words = [w.lower() for w in words]
    words[0] = words[0].capitalize()
    return ' '.join(words)


def sort_dict_by_key(d: dict) -> dict:
    return dict(sorted(d.items()))


def get_code_intent(level: int):
    return ' ' * 4 * level


def join_code(lines: List[str]) -> str:
    return '\n'.join(lines)


def get_sync_async_keywords(*, sync: bool) -> Tuple[str, str]:
    definition, call = 'async ', 'await '
    if sync:
        definition, call = '', ''

    return definition, call


def capitalize_first_symbol(string: str) -> str:
    if string and string[0].islower():
        chars = [c for c in string[1:]]
        chars.insert(0, string[0].upper())
        string = ''.join(chars)

    return string

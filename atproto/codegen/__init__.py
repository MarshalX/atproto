import re
import subprocess
from pathlib import Path
from typing import List, Tuple


def format_code(filepath: Path) -> None:
    subprocess.run(['black', '--quiet', filepath])


def write_code(filepath: Path, code: str) -> None:
    with open(filepath, 'w', encoding='UTF-8') as f:
        f.write(code)


def convert_camel_case_to_snake_case(string: str) -> str:
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def sort_dict_by_key(d: dict) -> dict:
    return dict(sorted(d.items()))


def get_code_intent(level=1):
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

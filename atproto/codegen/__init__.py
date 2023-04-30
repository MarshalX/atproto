import re
from typing import List


def convert_camel_case_to_snake_case(string: str) -> str:
    s = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s).lower()


def sort_dict_by_key(d: dict) -> dict:
    return dict(sorted(d.items()))


def get_code_intent(level=1):
    return ' ' * 4 * level


def join_code(lines: List[str]) -> str:
    return '\n'.join(lines)

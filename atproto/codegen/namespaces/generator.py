import subprocess
from pathlib import Path
from typing import List, Union

from codegen import convert_camel_case_to_snake_case, sort_dict_by_key, join_code
from codegen import get_code_intent as _
from codegen.namespaces.builder import build_namespaces, MethodInfo, RecordInfo

_NAMESPACES_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'namespaces')
_NAMESPACES_SYNC_FILENAME = 'sync.py'
_NAMESPACES_ASYNC_FILENAME = 'async.py'

_NAMESPACE_SUFFIX = 'Namespace'
_RECORD_SUFFIX = 'RecordNamespace'


def _get_namespace_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_NAMESPACE_SUFFIX}'


def _get_record_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_RECORD_SUFFIX}'


def _get_namespace_imports() -> str:
    lines = [
        'from dataclasses import dataclass',
        'from xrpc_client.namespaces.base import NamespaceBase, DefaultNamespace',
    ]

    return join_code(lines)


def _get_namespace_class_def(name: str) -> str:
    lines = ['@dataclass', f'class {_get_namespace_name(name)}(NamespaceBase):']

    return join_code(lines)


def _get_sub_namespaces_block(sub_namespaces: dict) -> str:
    lines = []

    sub_namespaces = sort_dict_by_key(sub_namespaces)
    for sub_namespace in sub_namespaces.keys():
        lines.append(f"{_(1)}{sub_namespace}: '{_get_namespace_name(sub_namespace)}' = DefaultNamespace()")

    return join_code(lines)


def _get_post_init_method(sub_namespaces: dict) -> str:
    lines = [f'{_(1)}def __post_init__(self):']

    sub_namespaces = sort_dict_by_key(sub_namespaces)
    for sub_namespace in sub_namespaces.keys():
        lines.append(f'{_(2)}self.{sub_namespace} = {_get_namespace_name(sub_namespace)}(self._client)')

    return join_code(lines)


def _get_namespace_method_signature(method_info: MethodInfo, *, sync: bool) -> str:
    keyword = 'async def'
    if sync:
        keyword = 'def'

    name = convert_camel_case_to_snake_case(method_info.name)

    # TODO(MarshalX): impl

    args = 'self'
    return_type_hint = 'None'
    return f'{keyword} {name}({args}) -> {return_type_hint}: pass'


def _get_namespace_methods_block(methods_info: List[MethodInfo], sync: bool) -> str:
    lines = []

    methods_info.sort(key=lambda e: e.name)
    for method_info in methods_info:
        lines.append(f'{_(1)}{_get_namespace_method_signature(method_info, sync=sync)}')

    return join_code(lines)


def _get_namespace_records_block(records_info: List[RecordInfo]) -> str:
    lines = []

    records_info.sort(key=lambda e: e.name)
    for record_info in records_info:
        lines.append(f"{_(1)}{record_info.name}: '{_get_record_name(record_info.name)}' = DefaultNamespace()")

    return join_code(lines)


def _generate_namespace_in_output(namespace_tree: Union[dict, list], output: List[str], *, sync: bool) -> None:
    for node_name, sub_node in namespace_tree.items():
        if isinstance(sub_node, dict):
            output.append(_get_namespace_class_def(node_name))
            output.append(_get_sub_namespaces_block(sub_node))
            output.append(_get_post_init_method(sub_node))

            _generate_namespace_in_output(sub_node, output, sync=sync)

        if isinstance(sub_node, list):
            output.append(_get_namespace_class_def(node_name))

            records = [info for info in sub_node if isinstance(info, RecordInfo)]
            output.append(_get_namespace_records_block(records))

            # TODO(MarshalX): generate namespace record classes!

            methods = [info for info in sub_node if isinstance(info, MethodInfo)]
            output.append(_get_namespace_methods_block(methods, sync=sync))


def _format_code(filepath: Path) -> None:
    subprocess.run(['black', '--quiet', filepath])


def _write_code(filepath: Path, code: str) -> None:
    with open(filepath, 'w', encoding='UTF-8') as f:
        f.write(code)


def generate_namespaces() -> None:
    namespace_tree = build_namespaces()

    for sync in (True, False):
        generated_code_lines_buffer = []
        _generate_namespace_in_output(namespace_tree, generated_code_lines_buffer, sync=sync)

        code = join_code([_get_namespace_imports(), *generated_code_lines_buffer])

        filename = _NAMESPACES_SYNC_FILENAME if sync else _NAMESPACES_ASYNC_FILENAME
        filepath = _NAMESPACES_OUTPUT_DIR.joinpath(filename)

        _write_code(filepath, code)
        _format_code(filepath)

        # TODO(MarshalX): generate ClientRaw as root of namespaces


if __name__ == '__main__':
    generate_namespaces()

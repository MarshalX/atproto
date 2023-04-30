import subprocess
from pathlib import Path
from typing import Callable, List, Set, Union

from codegen import convert_camel_case_to_snake_case
from codegen import get_code_intent as _
from codegen import get_sync_async_keywords, join_code, sort_dict_by_key
from codegen.models.generator import (
    get_data_model_name,
    get_options_model_name,
    get_params_model_name,
    get_response_model_name,
)
from codegen.namespaces.builder import MethodInfo, RecordInfo, build_namespaces
from lexicon.models import LexDefinitionType, LexObject

_NAMESPACES_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'namespaces')
_NAMESPACES_CLIENT_FILE_PATH = _NAMESPACES_OUTPUT_DIR.joinpath('client', 'raw.py')

_NAMESPACES_SYNC_FILENAME = 'sync.py'
_NAMESPACES_ASYNC_FILENAME = 'async.py'

_NAMESPACE_SUFFIX = 'Namespace'
_RECORD_SUFFIX = 'RecordNamespace'


def get_namespace_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_NAMESPACE_SUFFIX}'


def get_record_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_RECORD_SUFFIX}'


def _get_namespace_imports() -> str:
    lines = [
        # isort formatted
        'from dataclasses import dataclass',
        'from typing import Optional, Union',
        '',
        'from xrpc_client.models import get_or_create_model',
        'from xrpc_client.namespaces.base import DefaultNamespace, NamespaceBase',
    ]

    return join_code(lines)


def _get_namespace_class_def(name: str) -> str:
    lines = ['@dataclass', f'class {get_namespace_name(name)}(NamespaceBase):']

    return join_code(lines)


def _get_sub_namespaces_block(sub_namespaces: dict) -> str:
    lines = []

    sub_namespaces = sort_dict_by_key(sub_namespaces)
    for sub_namespace in sub_namespaces.keys():
        lines.append(f"{_(1)}{sub_namespace}: '{get_namespace_name(sub_namespace)}' = DefaultNamespace()")

    return join_code(lines)


def _get_post_init_method(sub_namespaces: dict) -> str:
    lines = [f'{_(1)}def __post_init__(self):']

    sub_namespaces = sort_dict_by_key(sub_namespaces)
    for sub_namespace in sub_namespaces.keys():
        lines.append(f'{_(2)}self.{sub_namespace} = {get_namespace_name(sub_namespace)}(self._client)')

    return join_code(lines)


def _get_namespace_method_body(method_info: MethodInfo, *, sync: bool) -> str:
    d, c = get_sync_async_keywords(sync=sync)

    lines = []

    presented_args = _get_namespace_method_signature_args_names(method_info)
    presented_args.remove('self')

    def _override_arg_line(name: str, model_name: str) -> str:
        # TODO(Marshal): temp. return real type when model will be generated
        return f'{_(2)}{name} = get_or_create_model({name}, \'models.{model_name}\')'
        # return f'{_(2)}{name} = get_or_create_model({name}, models.{model_name})'

    if 'params' in presented_args:
        lines.append(_override_arg_line('params', get_params_model_name(method_info.name)))
    elif 'data' in presented_args:
        lines.append(_override_arg_line('data', get_data_model_name(method_info.name)))
    elif 'options' in presented_args:
        lines.append(_override_arg_line('options', get_options_model_name(method_info.name)))

    invoke_args = [f'{k}={k}' for k in presented_args]
    invoke_args.insert(0, f"'{method_info.nsid}'")
    invoke_args = ', '.join(invoke_args)

    lines.append(f"{_(2)}{c}self._client.invoke({invoke_args})")

    return join_code(lines)


def _get_namespace_method_signature_arg(
    name: str, method_name: str, get_model_name: Callable, *, optional: bool
) -> str:
    default_value = ''
    type_hint = f"Union[dict, 'models.{get_model_name(method_name)}']"
    if optional:
        type_hint = f'Optional[{type_hint}]'
        default_value = ' = None'

    return f'{name}: {type_hint}{default_value}'


def _get_namespace_method_signature_args_names(method_info: MethodInfo) -> Set[str]:
    args = {'self'}
    if method_info.definition.parameters:
        args.add('params')
    if method_info.definition.type is LexDefinitionType.PROCEDURE and method_info.definition.input:
        schema = method_info.definition.input.schema
        if schema:
            args.add('data')
        # TODO(MarshalX): when be ready
        # args.append('options')

    return args


def _get_namespace_method_signature_args(method_info: MethodInfo) -> str:
    args = ['self']

    def is_optional_arg(lex_obj) -> bool:
        return lex_obj.required is None or len(lex_obj.required) == 0

    name = method_info.name

    if method_info.definition.parameters:
        params = method_info.definition.parameters
        optional = is_optional_arg(params)

        args.append(_get_namespace_method_signature_arg('params', name, get_params_model_name, optional=optional))

    if method_info.definition.type is LexDefinitionType.PROCEDURE and method_info.definition.input:
        schema = method_info.definition.input.schema
        if schema:
            optional = is_optional_arg(schema)

            # TODO(MarshalX): could LexRefVariant? For records?
            if schema and isinstance(schema, LexObject):
                args.append(_get_namespace_method_signature_arg('data', name, get_data_model_name, optional=optional))

        # TODO Options
        #   encoding? + custom like timeout

    # TODO(MarshalX): sort args by existing of default value
    #   for now there is no cases where PROCEDURE has parameters
    return ', '.join(args)


def _get_namespace_method_signature(method_info: MethodInfo, *, sync: bool) -> str:
    d, c = get_sync_async_keywords(sync=sync)
    name = convert_camel_case_to_snake_case(method_info.name)

    args = _get_namespace_method_signature_args(method_info)
    return_type_hint = f"'models.{get_response_model_name(method_info.name)}'"

    return f'{_(1)}{d}def {name}({args}) -> {return_type_hint}:'


def _get_namespace_methods_block(methods_info: List[MethodInfo], sync: bool) -> str:
    lines = []

    methods_info.sort(key=lambda e: e.name)
    for method_info in methods_info:
        lines.append(_get_namespace_method_signature(method_info, sync=sync))
        lines.append(_get_namespace_method_body(method_info, sync=sync))

    return join_code(lines)


def _get_namespace_records_block(records_info: List[RecordInfo]) -> str:
    lines = []

    records_info.sort(key=lambda e: e.name)
    for record_info in records_info:
        lines.append(f"{_(1)}{record_info.name}: '{get_record_name(record_info.name)}' = DefaultNamespace()")

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

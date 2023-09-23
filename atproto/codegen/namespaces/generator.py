import typing as t
from pathlib import Path

from atproto.codegen import (
    DISCLAIMER,
    INPUT_DICT,
    INPUT_MODEL,
    OUTPUT_MODEL,
    PARAMS_DICT,
    PARAMS_MODEL,
    _resolve_nsid_ref,
    convert_camel_case_to_snake_case,
    format_code,
    gen_description_by_camel_case_name,
    get_import_path,
    get_sync_async_keywords,
    join_code,
    sort_dict_by_key,
    write_code,
)
from atproto.codegen import get_code_intent as _
from atproto.codegen.namespaces.builder import MethodInfo, ProcedureInfo, QueryInfo, RecordInfo, build_namespaces
from atproto.lexicon.models import (
    LexObject,
    LexRef,
    LexXrpcProcedure,
    LexXrpcQuery,
)
from atproto.nsid import NSID

_NAMESPACES_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'namespaces')

_NAMESPACES_SYNC_FILENAME = 'sync_ns.py'
_NAMESPACES_ASYNC_FILENAME = 'async_ns.py'

_NAMESPACE_SUFFIX = 'Namespace'
_RECORD_SUFFIX = 'RecordNamespace'


def get_namespace_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_NAMESPACE_SUFFIX}'


def get_record_name(path_part: str) -> str:
    return f'{path_part.capitalize()}{_RECORD_SUFFIX}'


def _get_namespace_imports() -> str:
    lines = [
        DISCLAIMER,
        'import typing as t',
        '',
        'from atproto.xrpc_client import models',
        'from atproto.xrpc_client.models.utils import get_or_create, get_response_model',
        'from atproto.xrpc_client.namespaces.base import AsyncNamespaceBase, DefaultNamespace, NamespaceBase',
        '',
        'if t.TYPE_CHECKING:',
        f'{_(1)}from atproto.xrpc_client.client.async_raw import AsyncClientRaw',
        f'{_(1)}from atproto.xrpc_client.client.raw import ClientRaw',
    ]

    return join_code(lines)


def _get_namespace_class_def(name: str, *, sync: bool) -> str:
    base_class = 'NamespaceBase' if sync else 'AsyncNamespaceBase'
    lines = [f'class {get_namespace_name(name)}({base_class}):']

    return join_code(lines)


def _get_init_method(sub_namespaces: dict, *, sync: bool) -> str:
    client_typehint = "'ClientRaw'" if sync else "'AsyncClientRaw'"
    lines = [f'{_(1)}def __init__(self, client: {client_typehint}) -> None:', f'{_(2)}super().__init__(client)']

    sub_namespaces = sort_dict_by_key(sub_namespaces)
    for sub_namespace in sub_namespaces:
        lines.append(f'{_(2)}self.{sub_namespace} = {get_namespace_name(sub_namespace)}(self._client)')

    # TODO(MarshalX): add support for records

    return join_code(lines)


def _get_method_docstring(method_info: MethodInfo) -> str:
    method_desc = f'{gen_description_by_camel_case_name(method_info.name)}.'
    if method_info.definition.description:
        method_desc = method_info.definition.description
    if method_desc[-1] not in {'.', '?', '!'}:
        method_desc += '.'

    doc_string = [f'{_(2)}"""{method_desc}', '', f'{_(2)}Args:']

    presented_args = _get_namespace_method_signature_args_names(method_info.definition)
    if 'params' in presented_args:
        doc_string.append(f'{_(3)}params: Parameters.')
    if 'data_schema' in presented_args:
        doc_string.append(f'{_(3)}data: Input data.')
    if 'data_alias' in presented_args:
        doc_string.append(f'{_(3)}data: Input data alias.')

    doc_string.append(f'{_(3)}**kwargs: Arbitrary arguments to HTTP request.')
    doc_string.append('')

    doc_string.append(f'{_(2)}Returns:')

    return_type, __ = _get_namespace_method_return_type(method_info)

    return_type_desc = 'Output model'
    if return_type == 'bool':
        return_type_desc = 'Success status'

    doc_string.append(f'{_(3)}:obj:`{return_type}`: {return_type_desc}.')
    doc_string.append('')

    doc_string.append(f'{_(2)}Raises:')
    doc_string.append(f'{_(3)}:class:`atproto.exceptions.AtProtocolError`: Base exception.')

    doc_string.append(f'{_(2)}"""')
    doc_string.append('')

    return join_code(doc_string)


@t.overload
def _get_namespace_method_body(method_info: ProcedureInfo, *, sync: bool) -> str:
    ...


@t.overload
def _get_namespace_method_body(method_info: QueryInfo, *, sync: bool) -> str:
    ...


def _get_namespace_method_body(method_info: MethodInfo, *, sync: bool) -> str:
    d, c = get_sync_async_keywords(sync=sync)

    lines = [_get_method_docstring(method_info)]

    presented_args = _get_namespace_method_signature_args_names(method_info.definition)
    presented_args.remove('self')

    def _override_arg_line(name: str, model_name: str) -> str:
        model_path = f'models.{get_import_path(method_info.nsid)}.{model_name}'
        return f'{_(2)}{name}_model = get_or_create({name}, {model_path})'

    invoke_args = [f"'{method_info.nsid}'"]

    if 'params' in presented_args:
        invoke_args.append('params=params_model')
        lines.append(_override_arg_line('params', PARAMS_MODEL))
    if 'data_schema' in presented_args:
        invoke_args.append('data=data_model')
        lines.append(_override_arg_line('data', INPUT_MODEL))
    if 'data_alias' in presented_args:
        invoke_args.append('data=data')
    if 'input_encoding' in presented_args:
        input_encoding = method_info.definition.input.encoding
        invoke_args.append(f"input_encoding='{input_encoding}'")
    if 'output_encoding' in presented_args:
        output_encoding = method_info.definition.output.encoding
        invoke_args.append(f"output_encoding='{output_encoding}'")

    invoke_args.append('**kwargs')
    invoke_args_str = ', '.join(invoke_args)

    method_name = 'invoke_query'
    if isinstance(method_info.definition, LexXrpcProcedure):
        method_name = 'invoke_procedure'

    lines.append(f'{_(2)}response = {c}self._client.{method_name}({invoke_args_str})')

    return_type, __ = _get_namespace_method_return_type(method_info)
    lines.append(f'{_(2)}return get_response_model(response, {return_type})')

    return join_code(lines)


def _get_namespace_method_signature_arg(
    name: str, nsid: NSID, model_name: t.Union[t.List[str], str], *, optional: bool, alias: bool = False
) -> str:
    if alias:
        return f"{name}: 'models.{get_import_path(nsid)}.{model_name}'"

    default_value = ''
    type_hint = (
        f"t.Union[dict, 'models.{get_import_path(nsid)}.{model_name}']"
        if isinstance(model_name, str)
        else 't.Union[' + ', '.join(f'models.{get_import_path(nsid)}.{i}' for i in model_name) + ']'
    )
    if optional:
        type_hint = f't.Optional[{type_hint}]'
        default_value = ' = None'

    return f'{name}: {type_hint}{default_value}'


def _get_namespace_method_signature_args_names(definition: t.Union[LexXrpcProcedure, LexXrpcQuery]) -> t.Set[str]:
    args = {'self'}
    if definition.parameters:
        args.add('params')

    if isinstance(definition, LexXrpcProcedure) and definition.input:
        if definition.input.schema:
            args.add('data_schema')
        else:
            args.add('data_alias')

        if definition.input.encoding:
            args.add('input_encoding')

    if definition.output and definition.output.encoding:
        args.add('output_encoding')

    return args


def _get_namespace_method_signature_args(method_info: MethodInfo) -> str:
    args = ['self']
    optional_args = []

    def _add_arg(arg_def: str, *, optional: bool) -> None:
        if optional:
            optional_args.append(arg_def)
        else:
            args.append(arg_def)

    def is_optional_arg(lex_obj) -> bool:
        return lex_obj.required is None or len(lex_obj.required) == 0

    if method_info.definition.parameters:
        params = method_info.definition.parameters
        is_optional = is_optional_arg(params)

        arg = _get_namespace_method_signature_arg(
            'params', method_info.nsid, [PARAMS_MODEL, PARAMS_DICT], optional=is_optional
        )
        _add_arg(arg, optional=is_optional)

    if isinstance(method_info, ProcedureInfo) and method_info.definition.input:
        schema = method_info.definition.input.schema
        if schema:
            is_optional = is_optional_arg(schema)

            if schema and isinstance(schema, LexObject):
                arg = _get_namespace_method_signature_arg(
                    'data', method_info.nsid, [INPUT_MODEL, INPUT_DICT], optional=is_optional
                )
                _add_arg(arg, optional=is_optional)
            else:
                raise ValueError(f'Bad type {type(schema)}')  # probably LexRefVariant
        else:
            arg = _get_namespace_method_signature_arg('data', method_info.nsid, INPUT_MODEL, optional=False, alias=True)
            _add_arg(arg, optional=False)

    args.extend(optional_args)
    args.append('**kwargs: t.Any')
    return ', '.join(args)


def _get_namespace_method_return_type(method_info: MethodInfo) -> t.Tuple[str, bool]:
    if method_info.definition.output and isinstance(method_info.definition.output.schema, LexRef):
        ref_class, _ = _resolve_nsid_ref(method_info.nsid, method_info.definition.output.schema.ref)
        return ref_class, True

    is_model = False
    return_type = 'bool'  # return success of response
    if method_info.definition.output:
        # example of methods without response: app.bsky.graph.muteActor, app.bsky.graph.muteActor
        is_model = True
        return_type = f'models.{get_import_path(method_info.nsid)}.{OUTPUT_MODEL}'

    return return_type, is_model


def _get_namespace_method_signature(method_info: MethodInfo, *, sync: bool) -> str:
    d, c = get_sync_async_keywords(sync=sync)

    name = convert_camel_case_to_snake_case(method_info.name)
    args = _get_namespace_method_signature_args(method_info)
    return_type, is_model = _get_namespace_method_return_type(method_info)

    if is_model:
        return_type = f"'{return_type}'"

    return f'{_(1)}{d}def {name}({args}) -> {return_type}:'


def _get_namespace_methods_block(methods_info: t.List[MethodInfo], sync: bool) -> str:
    lines = []

    methods_info.sort(key=lambda e: e.name)
    for method_info in methods_info:
        lines.append(_get_namespace_method_signature(method_info, sync=sync))
        lines.append(_get_namespace_method_body(method_info, sync=sync))

    return join_code(lines)


def _get_namespace_records_block(records_info: t.List[RecordInfo]) -> str:
    lines = []

    records_info.sort(key=lambda e: e.name)
    for record_info in records_info:
        lines.append(f"{_(1)}{record_info.name}: '{get_record_name(record_info.name)}' = DefaultNamespace()")

    return join_code(lines)


def _generate_namespace_in_output(namespace_tree: dict, output: t.List[str], *, sync: bool) -> None:
    for node_name, sub_node in namespace_tree.items():
        if isinstance(sub_node, dict):
            output.append(_get_namespace_class_def(node_name, sync=sync))
            output.append(_get_init_method(sub_node, sync=sync))

            _generate_namespace_in_output(sub_node, output, sync=sync)

        if isinstance(sub_node, list):
            output.append(_get_namespace_class_def(node_name, sync=sync))

            # TODO(MarshalX): gen namespace by RecordInfo later
            # TODO(MarshalX): generate namespace record classes!

            methods = [info for info in sub_node if isinstance(info, (ProcedureInfo, QueryInfo))]
            output.append(_get_namespace_methods_block(methods, sync=sync))


def generate_namespaces(
    lexicon_dir: t.Optional[Path] = None,
    output_dir: t.Optional[Path] = None,
    async_filename: t.Optional[str] = None,
    sync_filename: t.Optional[str] = None,
) -> None:
    if not output_dir:
        output_dir = _NAMESPACES_OUTPUT_DIR
    if not async_filename:
        async_filename = _NAMESPACES_ASYNC_FILENAME
    if not sync_filename:
        sync_filename = _NAMESPACES_SYNC_FILENAME

    namespace_tree = build_namespaces(lexicon_dir)

    for sync in (True, False):
        generated_code_lines_buffer: t.List[str] = []
        _generate_namespace_in_output(namespace_tree, generated_code_lines_buffer, sync=sync)

        code = join_code([_get_namespace_imports(), *generated_code_lines_buffer])

        filename = sync_filename if sync else async_filename
        filepath = output_dir.joinpath(filename)

        write_code(filepath, code)

    # TODO(MarshalX): generate ClientRaw as root of namespaces

    format_code(output_dir)

import os
from enum import Enum
from pathlib import Path
from typing import Tuple, Union

from atproto.codegen import (
    DISCLAIMER,
    INPUT_MODEL,
    OUTPUT_MODEL,
    PARAMS_MODEL,
    append_code,
    capitalize_first_symbol,
    format_code,
    gen_description_by_camel_case_name,
)
from atproto.codegen import get_code_intent as _
from atproto.codegen import get_file_path_parts, get_import_path, join_code, write_code
from atproto.codegen.models import builder
from atproto.exceptions import InvalidNsidError
from atproto.lexicon import models
from atproto.nsid import NSID

_MODELS_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'models')


class ModelType(Enum):
    PARAMS = 'Parameters'
    DATA = 'Input data'
    RESPONSE = 'Output data'
    DEF = 'Definition'
    RECORD = 'Record'


def get_def_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}'


def get_model_path(nsid: NSID, method_name: str) -> str:
    return f'models.{get_import_path(nsid)}.{get_def_model_name(method_name)}'


def save_code(nsid: NSID, code: str) -> None:
    path_to_file = _MODELS_OUTPUT_DIR.joinpath(*get_file_path_parts(nsid))
    write_code(_MODELS_OUTPUT_DIR.joinpath(path_to_file), code)


def save_code_part(nsid: NSID, code: str) -> None:
    path_to_file = _MODELS_OUTPUT_DIR.joinpath(*get_file_path_parts(nsid))
    append_code(_MODELS_OUTPUT_DIR.joinpath(path_to_file), code)


def _get_model_imports() -> str:
    # TODO(MarshalX): isort can't delete unused imports. mb add ruff
    lines = [
        'from dataclasses import dataclass',
        'from typing import TYPE_CHECKING, Any, Dict, List, Optional, Type, Union',
        '',
        'from typing_extensions import Literal',
        'from atproto.xrpc_client import models',
        'from atproto.xrpc_client.models import base',
        'from atproto.xrpc_client.models.blob_ref import BlobRef',
        '',
        'from atproto import CID',
        '',
    ]

    return join_code(lines)


_NSID_WITH_IMPORTS = set()


def _save_code_import_if_not_exist(nsid) -> None:
    if nsid not in _NSID_WITH_IMPORTS:
        lines = [DISCLAIMER, _get_model_imports()]
        save_code(nsid, join_code(lines))
        _NSID_WITH_IMPORTS.add(nsid)


def _get_model_class_def(name: str, model_type: ModelType) -> str:
    lines = ['@dataclass']

    if model_type is ModelType.PARAMS:
        lines.append(f'class {PARAMS_MODEL}(base.ParamsModelBase):')
    elif model_type is ModelType.DATA:
        lines.append(f'class {INPUT_MODEL}(base.DataModelBase):')
    elif model_type is ModelType.RESPONSE:
        lines.append(f'class {OUTPUT_MODEL}(base.ResponseModelBase):')
    elif model_type is ModelType.RECORD:
        lines.append(f'class {get_def_model_name(name)}(base.RecordModelBase):')
    elif model_type is ModelType.DEF:
        lines.append(f'class {get_def_model_name(name)}(base.ModelBase):')

    lines.append('')

    return join_code(lines)


_LEXICON_TYPE_TO_PRIMITIVE_TYPEHINT = {
    models.LexString: 'str',
    models.LexInteger: 'int',
    models.LexBoolean: 'bool',
}


def _get_optional_typehint(type_hint, *, optional: bool) -> str:
    if optional:
        return f'Optional[{type_hint}] = None'
    else:
        return type_hint


def _get_ref_typehint(nsid: NSID, field_type_def, *, optional: bool) -> str:
    model_path, _ = _resolve_nsid_ref(nsid, field_type_def.ref)
    return _get_optional_typehint(f"'{model_path}'", optional=optional)


def _resolve_nsid_ref(nsid: NSID, ref: str, *, local: bool = False) -> Tuple[str, str]:
    """Returns path to the model and model name"""
    if '#' in ref:
        ref_nsid_str, def_name = ref.split('#', 1)
        def_name = get_def_model_name(def_name)

        try:
            ref_nsid = NSID.from_str(ref_nsid_str)
            return get_model_path(ref_nsid, def_name), def_name
        except InvalidNsidError:
            if local:
                return def_name, def_name
            return get_model_path(nsid, def_name), def_name
    else:
        ref_nsid = NSID.from_str(ref)
        def_name = get_def_model_name(nsid.name)

        if local:
            return def_name, def_name

        # FIXME(MarshalX): Is it works well? ;d
        return get_model_path(ref_nsid, 'Main'), def_name
        # return get_model_path(ref_nsid, ref_nsid.name), def_name


def _get_ref_union_typehint(nsid: NSID, field_type_def, *, optional: bool) -> str:
    def_names = []
    for ref in field_type_def.refs:
        import_path, _ = _resolve_nsid_ref(nsid, ref)
        def_names.append(import_path)

    # unbelievable but it's true. If schema doesn't describe the right type in Union
    # we should fall back to the plain data
    # maybe it's for the records that have custom fields... idk
    # ref: https://github.com/bluesky-social/atproto/blob/b01e47b61730d05a780f7a42667b91ccaa192e8e/packages/lex-cli/src/codegen/lex-gen.ts#L325
    # grep by "{$type: string; [k: string]: unknown}" string
    def_names.append('Dict[str, Any]')

    def_names = ', '.join([f"'{name}'" for name in def_names])
    return _get_optional_typehint(f"Union[{def_names}]", optional=optional)


def _get_model_field_typehint(nsid: NSID, field_name: str, field_type_def, *, optional: bool) -> str:
    field_type = type(field_type_def)

    if field_type == models.LexUnknown:
        # TODO(MarshalX): some of "unknown" types are well known...
        return _get_optional_typehint(f"'base.RecordModelBase'", optional=optional)

    type_hint = _LEXICON_TYPE_TO_PRIMITIVE_TYPEHINT.get(field_type)
    if type_hint:
        return _get_optional_typehint(type_hint, optional=optional)

    if field_type is models.LexArray:
        items_type_hint = _get_model_field_typehint(nsid, field_name, field_type_def.items, optional=False)
        return _get_optional_typehint(f'List[{items_type_hint}]', optional=optional)

    if field_type is models.LexRef:
        return _get_ref_typehint(nsid, field_type_def, optional=optional)

    if field_type is models.LexRefUnion:
        return _get_ref_union_typehint(nsid, field_type_def, optional=optional)

    if field_type is models.LexCidLink:
        return _get_optional_typehint(f'CID', optional=optional)

    if field_type is models.LexBytes:
        # CAR file containing relevant blocks
        return _get_optional_typehint('Union[str, bytes]', optional=optional)

    if field_type is models.LexBlob:
        # yes, it returns blob,but actually it's blob ref here
        return _get_optional_typehint('BlobRef', optional=optional)

    raise ValueError(f'Unknown field type {field_name.__name__}')


def _get_req_fields_set(lex_obj: Union[models.LexObject, models.LexXrpcParameters]) -> set:
    required_fields = set()
    if lex_obj.required:
        required_fields = set(lex_obj.required)

    if hasattr(lex_obj, 'nullable') and lex_obj.nullable:
        # TODO(MarshalX): not 100% the same thing. think about it
        required_fields = required_fields.difference(set(lex_obj.nullable))

    return required_fields


def _get_model_docstring(
    nsid: Union[str, NSID], lex_object: Union[models.LexObject, models.LexXrpcParameters], model_type: ModelType
) -> str:
    model_desc = lex_object.description or ''
    model_desc = f"{model_type.value} model for :obj:`{nsid}`. {model_desc}"

    doc_string = [f'{_(1)}"""{model_desc}', '', f'{_(1)}Attributes:']

    for field_name, field_type in lex_object.properties.items():
        field_desc = field_type.description
        if field_desc is None:
            field_desc = gen_description_by_camel_case_name(field_name)
        if field_desc[-1] not in {'.', '?', '!'}:
            field_desc += '.'

        doc_string.append(f'{_(2)}{field_name}: {field_desc}')

    doc_string.append(f'{_(1)}"""')
    doc_string.append('')

    return join_code(doc_string)


def _get_model(nsid: NSID, lex_object: Union[models.LexObject, models.LexXrpcParameters]) -> str:
    required_fields = _get_req_fields_set(lex_object)

    fields = []
    optional_fields = []

    for field_name, field_type in lex_object.properties.items():
        is_optional = field_name not in required_fields
        type_hint = _get_model_field_typehint(nsid, field_name, field_type, optional=is_optional)

        field_def = f'{_(1)}{field_name}: {type_hint}'  # TODO(MarshalX): Add default values. for bool, etc..
        if is_optional:
            optional_fields.append(field_def)
        else:
            fields.append(field_def)

    optional_fields.sort()
    fields.sort()

    fields.extend(optional_fields)

    fields.append('')

    return join_code(fields)


def _get_model_ref(nsid: NSID, ref: models.LexRef) -> str:
    # FIXME(MarshalX): "local=True" Is it works well? ;d
    ref_class, _ = _resolve_nsid_ref(nsid, ref.ref, local=True)
    ref_typehint = f'Type[{ref_class}]'

    # "Ref" suffix required to fix name collisions from different namespaces
    lines = [
        f'#: {OUTPUT_MODEL} reference to :obj:`{ref_class}` model.',
        f'{OUTPUT_MODEL}Ref: {ref_typehint} = {ref_class}',
        '',
        '',
    ]

    return join_code(lines)


def _get_model_raw_data(name: str) -> str:
    lines = [f'#: {name} raw data type.', f'{name}: Union[Type[str], Type[bytes]] = bytes\n\n']
    return join_code(lines)


def _generate_params_model(nsid: NSID, definition: Union[models.LexXrpcProcedure, models.LexXrpcQuery]) -> str:
    lines = [_get_model_class_def(nsid.name, ModelType.PARAMS)]

    if definition.parameters:
        lines.append(_get_model_docstring(nsid, definition.parameters, ModelType.PARAMS))
        lines.append(_get_model(nsid, definition.parameters))

    return join_code(lines)


def _generate_xrpc_body_model(nsid: NSID, body: models.LexXrpcBody, model_type: ModelType) -> str:
    lines = []
    if body.schema:
        if isinstance(body.schema, models.LexObject):
            lines.append(_get_model_class_def(nsid.name, model_type))
            lines.append(_get_model_docstring(nsid, body.schema, model_type))
            lines.append(_get_model(nsid, body.schema))
    else:
        if model_type is ModelType.DATA:
            model_name = INPUT_MODEL
        elif model_type is ModelType.RESPONSE:
            model_name = OUTPUT_MODEL
        else:
            raise ValueError('Wrong type or not implemented')

        lines.append(_get_model_raw_data(model_name))

    return join_code(lines)


def _generate_data_model(nsid: NSID, input_body: models.LexXrpcBody) -> str:
    return _generate_xrpc_body_model(nsid, input_body, ModelType.DATA)


def _generate_response_model(nsid: NSID, output_body: models.LexXrpcBody) -> str:
    return _generate_xrpc_body_model(nsid, output_body, ModelType.RESPONSE)


def _generate_def_model(nsid: NSID, def_name: str, def_model: models.LexObject, model_type: ModelType) -> str:
    lines = [
        _get_model_class_def(def_name, model_type),
        _get_model_docstring(nsid, def_model, model_type),
        _get_model(nsid, def_model),
    ]

    if def_name == 'main':
        lines.append(f"{_(1)}_type: str = '{nsid}'")

    lines.append('')

    return join_code(lines)


def _generate_def_token(def_name: str) -> str:
    lines = [
        f"{get_def_model_name(def_name)}: Literal['{def_name}'] = '{def_name}'",
        '',
        '',
    ]
    return join_code(lines)


def _generate_def_string(def_name: str, def_model: models.LexString) -> str:
    # FIXME(MarshalX): Doesn't support all fields

    if not def_model.knownValues:
        return ''

    # FIXME(MarshalX): Use ref resolver
    known_values = ["'" + get_def_model_name(v.split('#', 1)[1]) + "'" for v in def_model.knownValues]
    known_values = ', '.join(known_values)

    type_ = f'Literal[{known_values}]'

    lines = [
        f"{get_def_model_name(def_name)} = {type_}",
        '',
        '',
    ]

    return join_code(lines)


def _generate_params_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        definition = defs['main']
        if definition.parameters:
            save_code_part(nsid, _generate_params_model(nsid, definition))


def _generate_data_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        definition = defs['main']
        if definition.input:
            save_code_part(nsid, _generate_data_model(nsid, definition.input))


def _generate_response_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        definition = defs['main']
        if definition.output:
            save_code_part(nsid, _generate_response_model(nsid, definition.output))


def _generate_def_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_model in defs.items():
            if isinstance(def_model, models.LexToken):
                save_code_part(nsid, _generate_def_token(def_name))
            if isinstance(def_model, models.LexString):
                save_code_part(nsid, _generate_def_string(def_name, def_model))
            if isinstance(def_model, models.LexObject):
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_model, ModelType.DEF))


def _generate_record_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            if isinstance(def_record, models.LexRecord):
                # TODO(MarshalX): Process somehow def_record.key?
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_record.record, ModelType.RECORD))


def _generate_record_type_database(lex_db: builder.LexDB) -> None:
    lines = ['from atproto.xrpc_client import models', 'RECORD_TYPE_TO_MODEL_CLASS = {']

    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            # for now there are records only in under "main" definition name.
            # need to rework a bit if this behaviour will be changed
            if isinstance(def_record, models.LexRecord):
                class_name = get_def_model_name(def_name)
                record_type = str(nsid)

                path_to_class = f'models.{get_import_path(nsid)}.{class_name}'

                lines.append(f"'{record_type}': {path_to_class},")

    lines.append('}')

    write_code(_MODELS_OUTPUT_DIR.joinpath('type_conversion.py'), join_code(lines))


def _generate_ref_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        definition = defs['main']
        if hasattr(definition, 'input') and definition.input and definition.input.schema:
            if isinstance(definition.input.schema, models.LexRef):
                save_code_part(nsid, _get_model_ref(nsid, definition.input.schema))

        if hasattr(definition, 'output') and definition.output and definition.output.schema:
            if isinstance(definition.output.schema, models.LexRef):
                save_code_part(nsid, _get_model_ref(nsid, definition.output.schema))


def _generate_init_files(root_package_path: Path) -> None:
    # one of the ways that I tried. Doesn't work well due to circular imports
    for root, dirs, files in os.walk(root_package_path):
        root = Path(root)

        import_lines = []
        for dir_name in dirs:
            if dir_name.startswith('__'):
                continue

            import_parts = root.parts[root.joinpath(dir_name).parts.index('xrpc_client') :]
            from_import = '.'.join(import_parts)

            if dir_name in {'app', 'com'}:
                continue

            import_lines.append(f'from {from_import} import {dir_name}')

        for file_name in files:
            if file_name.startswith('__'):
                continue

            import_parts = root.parts[root.parts.index('xrpc_client') :]
            from_import = '.'.join(import_parts)

            import_lines.append(f'from atproto.{from_import} import {file_name[:-3]}')

        if root.name == 'models':
            # FIXME skip for now. should be generated too
            continue

        if root.name == '__pycache__':
            continue

        write_code(root.joinpath('__init__.py'), join_code(import_lines))


def _generate_empty_init_files(root_package_path: Path):
    for root, dirs, files in os.walk(root_package_path):
        root = Path(root)

        for dir_name in dirs:
            if dir_name.startswith('__'):
                continue

            if dir_name in {'app', 'com'}:
                continue

        for file_name in files:
            if file_name.startswith('__'):
                continue

        if root.name == 'models':
            # FIXME skip for now. should be generated too
            continue

        if root.name == '__pycache__':
            continue

        write_code(root.joinpath('__init__.py'), DISCLAIMER)


def _generate_import_aliases(root_package_path: Path):
    # is generates __init__.py file if models dir with aliases like this;
    # from xrpc_client.models.app.bsky.actor import defs as AppBskyActorDefs

    import_lines = []
    for root, dirs, files in os.walk(root_package_path):
        root = Path(root)

        if root == root_package_path:
            continue

        for file in files:
            if file.startswith('.') or file.startswith('__') or file.endswith('.pyc'):
                continue

            import_parts = root.parts[root.parts.index('xrpc_client') :]
            from_import = '.'.join(import_parts)

            nsid_parts = list(root.parts[root.parts.index('models') + 1 :]) + file[:-3].split('_')
            alias_name = ''.join([p.capitalize() for p in nsid_parts])

            import_lines.append(f'from atproto.{from_import} import {file[:-3]} as {alias_name}')

    write_code(_MODELS_OUTPUT_DIR.joinpath('__init__.py'), join_code(import_lines))


def generate_models():
    _generate_params_models(builder.build_params_models())
    _generate_data_models(builder.build_data_models())
    _generate_response_models(builder.build_response_models())
    _generate_def_models(builder.build_def_models())

    _generate_record_models(builder.build_record_models())
    _generate_record_type_database(builder.build_record_models())

    # refs should be generated at the end!
    _generate_ref_models(builder.build_refs_models())

    _generate_empty_init_files(_MODELS_OUTPUT_DIR)
    _generate_import_aliases(_MODELS_OUTPUT_DIR)

    format_code(_MODELS_OUTPUT_DIR)

    print('Done')


if __name__ == '__main__':
    generate_models()

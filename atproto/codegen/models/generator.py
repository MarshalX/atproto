import os
import typing as t
from enum import Enum
from pathlib import Path

from atproto.codegen import (
    DISCLAIMER,
    INPUT_MODEL,
    OUTPUT_MODEL,
    PARAMS_MODEL,
    _resolve_nsid_ref,
    append_code,
    format_code,
    gen_description_by_camel_case_name,
    get_def_model_name,
    get_file_path_parts,
    get_import_path,
    join_code,
    write_code,
)
from atproto.codegen import get_code_intent as _
from atproto.codegen.models import builder
from atproto.lexicon import models
from atproto.nsid import NSID

_MODELS_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'models')


class ModelType(Enum):
    PARAMS = 'Parameters'
    DATA = 'Input data'
    RESPONSE = 'Output data'
    DEF = 'Definition'
    RECORD = 'Record'


def save_code(nsid: NSID, code: str) -> None:
    path_to_file = _MODELS_OUTPUT_DIR.joinpath(*get_file_path_parts(nsid))
    write_code(_MODELS_OUTPUT_DIR.joinpath(path_to_file), code)


def save_code_part(nsid: NSID, code: str) -> None:
    path_to_file = _MODELS_OUTPUT_DIR.joinpath(*get_file_path_parts(nsid))
    append_code(_MODELS_OUTPUT_DIR.joinpath(path_to_file), code)


def _get_model_imports() -> str:
    # we are using ruff with F401 autofix to delete unused imports
    lines = [
        'import typing as t',
        '',
        'import typing_extensions as te',
        'from pydantic import Field',
        '',
        'if t.TYPE_CHECKING:',
        f'{_(1)}from atproto.xrpc_client import models',
        f'{_(1)}from atproto.xrpc_client.models.blob_ref import BlobRef',
        f'{_(1)}from atproto import CID',
        'from atproto.xrpc_client.models import base',
        'from atproto.xrpc_client.models import unknown_type',
        '',
        '',
    ]

    return join_code(lines)


_NSID_WITH_IMPORTS = set()


def _save_code_import_if_not_exist(nsid: NSID) -> None:
    if nsid not in _NSID_WITH_IMPORTS:
        lines = [DISCLAIMER, _get_model_imports()]
        save_code(nsid, join_code(lines))
        _NSID_WITH_IMPORTS.add(nsid)


def _get_model_class_def(name: str, model_type: ModelType) -> str:
    lines = []

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


def _get_optional_typehint(type_hint, *, optional: bool, with_value: bool = True) -> str:
    value = ' = None' if with_value else ''
    if optional:
        return f't.Optional[{type_hint}]{value}'
    return type_hint


def _get_ref_typehint(nsid: NSID, field_type_def, *, optional: bool) -> str:
    model_path, _ = _resolve_nsid_ref(nsid, field_type_def.ref)
    return _get_optional_typehint(f"'{model_path}'", optional=optional)


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
    # TODO(MarshalX): use 'base.UnknownDict' and convert to DotDict
    # def_names.append('t.Dict[str, t.Any]')  # FIXME(MarshalX): support pydantic

    def_names = ', '.join([f"'{name}'" for name in def_names])
    def_field_meta = 'Field(default=None, discriminator="py_type")' if optional else 'Field(discriminator="py_type")'

    annotated_union = f'te.Annotated[t.Union[{def_names}], {def_field_meta}]'
    return _get_optional_typehint(annotated_union, optional=optional)


def _get_model_field_typehint(nsid: NSID, field_name: str, field_type_def, *, optional: bool) -> str:
    field_type = type(field_type_def)

    if field_type == models.LexUnknown:
        # unknown type is a generic response with records or any not described type in the lexicon. for example, didDoc
        return _get_optional_typehint("'unknown_type.UnknownType'", optional=optional)

    type_hint = _LEXICON_TYPE_TO_PRIMITIVE_TYPEHINT.get(field_type)
    if type_hint:
        return _get_optional_typehint(type_hint, optional=optional)

    if field_type is models.LexArray:
        items_type_hint = _get_model_field_typehint(nsid, field_name, field_type_def.items, optional=False)
        return _get_optional_typehint(f't.List[{items_type_hint}]', optional=optional)

    if field_type is models.LexRef:
        return _get_ref_typehint(nsid, field_type_def, optional=optional)

    if field_type is models.LexRefUnion:
        return _get_ref_union_typehint(nsid, field_type_def, optional=optional)

    if field_type is models.LexCidLink:
        return _get_optional_typehint("'CID'", optional=optional)

    if field_type is models.LexBytes:
        # CAR file containing relevant blocks
        return _get_optional_typehint('t.Union[str, bytes]', optional=optional)

    if field_type is models.LexBlob:
        # yes, it returns blob,but actually it's blob ref here
        return _get_optional_typehint("'BlobRef'", optional=optional)

    raise ValueError(f'Unknown field type {field_type.__name__}')


def _get_req_fields_set(lex_obj: t.Union[models.LexObject, models.LexXrpcParameters]) -> set:
    required_fields = set()
    if lex_obj.required:
        required_fields = set(lex_obj.required)

    if hasattr(lex_obj, 'nullable') and lex_obj.nullable:
        # TODO(MarshalX): not 100% the same thing. think about it
        required_fields = required_fields.difference(set(lex_obj.nullable))

    return required_fields


def _get_field_docstring(field_name: str, field_type) -> str:
    field_desc = field_type.description
    if field_desc is None:
        field_desc = gen_description_by_camel_case_name(field_name)
    if field_desc[-1] not in {'.', '?', '!'}:
        field_desc += '.'

    return field_desc


def _get_model_docstring(
    nsid: t.Union[str, NSID],
    lex_object: t.Union[models.LexXrpcQuery, models.LexSubscription, models.LexObject, models.LexXrpcParameters],
    model_type: ModelType,
) -> str:
    model_desc = lex_object.description or ''
    model_desc = f'{model_type.value} model for :obj:`{nsid}`. {model_desc}'

    doc_string = [f'{_(1)}"""{model_desc}"""', '']

    return join_code(doc_string)


def _get_model(nsid: NSID, lex_object: t.Union[models.LexObject, models.LexXrpcParameters]) -> str:
    required_fields = _get_req_fields_set(lex_object)

    fields = []
    optional_fields = []

    for field_name, field_type in lex_object.properties.items():
        is_optional = field_name not in required_fields
        type_hint = _get_model_field_typehint(nsid, field_name, field_type, optional=is_optional)
        description = _get_field_docstring(field_name, field_type)

        # TODO(MarshalX): Add default values. for bool, etc..
        field_def = f'{_(1)}{field_name}: {type_hint} #: {description}'
        if is_optional:
            optional_fields.append(field_def)
        else:
            fields.append(field_def)

    optional_fields.sort()
    fields.sort()

    fields.extend(optional_fields)

    fields.append('')

    return join_code(fields)


def _get_model_raw_data(name: str) -> str:
    lines = [f'#: {name} raw data type.', f'{name}: te.TypeAlias = bytes\n\n']
    return join_code(lines)


def _generate_params_model(nsid: NSID, definition: t.Union[models.LexXrpcQuery, models.LexSubscription]) -> str:
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

    def_type = f'{nsid}#{def_name}'
    if def_name == 'main':
        def_type = str(nsid)

    lines.append(f"{_(1)}py_type: te.Literal['{def_type}'] = Field(default='{def_type}', alias='$type')")
    lines.append('')

    return join_code(lines)


def _generate_def_token(def_name: str) -> str:
    lines = [
        f"{get_def_model_name(def_name)}: te.Literal['{def_name}'] = '{def_name}'",
        '',
        '',
    ]
    return join_code(lines)


def _generate_def_array(nsid: NSID, def_name: str, def_model: models.LexArray) -> str:
    return f'{get_def_model_name(def_name)} = {_get_model_field_typehint(nsid, def_name, def_model, optional=False)}\n'


def _generate_def_string(def_name: str, def_model: models.LexString) -> str:
    # FIXME(MarshalX): Doesn't support all fields

    if not def_model.knownValues:
        return ''

    # FIXME(MarshalX): Use ref resolver
    known_values_list = ["'" + get_def_model_name(v.split('#', 1)[1]) + "'" for v in def_model.knownValues]
    known_values = ', '.join(known_values_list)

    type_ = f'te.Literal[{known_values}]'

    lines = [
        f'{get_def_model_name(def_name)} = {type_}',
        '',
        '',
    ]

    return join_code(lines)


def _generate_params_models(lex_db: builder.BuiltParamsModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        definition = defs['main']
        if definition.parameters:
            if isinstance(definition.parameters, models.LexXrpcParameters):
                save_code_part(nsid, _generate_params_model(nsid, definition))
            else:
                # LexXrpcProcedure has parameters using another model
                raise ValueError('Wrong parameters type or not implemented')


def _generate_data_models(lex_db: builder.BuiltDataModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        definition = defs['main']
        if definition.input:
            save_code_part(nsid, _generate_data_model(nsid, definition.input))


def _generate_response_models(lex_db: builder.BuiltResponseModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        definition = defs['main']
        if definition.output:
            save_code_part(nsid, _generate_response_model(nsid, definition.output))


def _generate_def_models(lex_db: builder.BuiltDefModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_model in defs.items():
            if isinstance(def_model, models.LexToken):
                save_code_part(nsid, _generate_def_token(def_name))
            elif isinstance(def_model, models.LexString):
                save_code_part(nsid, _generate_def_string(def_name, def_model))
            elif isinstance(def_model, models.LexObject):
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_model, ModelType.DEF))
            elif isinstance(def_model, models.LexArray):
                save_code_part(nsid, _generate_def_array(nsid, def_name, def_model))
            else:
                raise ValueError(f'Unhandled type {type(def_model)}')


def _generate_record_models(lex_db: builder.BuiltRecordModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            if isinstance(def_record, models.LexRecord):
                # TODO(MarshalX): Process somehow def_record.key?
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_record.record, ModelType.RECORD))


def _generate_record_type_database(lex_db: builder.BuiltRecordModels) -> None:
    type_conversion_lines = ['from atproto.xrpc_client import models', 'RECORD_TYPE_TO_MODEL_CLASS = {']
    unknown_record_type_hint_lines = [
        'import typing as t',
        'import typing_extensions as te',
        'from pydantic import Field',
        'if t.TYPE_CHECKING:',
        f'{_(4)}from atproto.xrpc_client.models import base',
        f'{_(4)}from atproto.xrpc_client import models',
        '',
        'UnknownRecordType: te.TypeAlias = t.Union[',
    ]
    unknown_record_type_pydantic_lines = ['UnknownRecordTypePydantic = te.Annotated[t.Union[']

    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            # for now there are records only in under "main" definition name.
            # need to rework a bit if this behaviour will be changed
            if isinstance(def_record, models.LexRecord):
                class_name = get_def_model_name(def_name)
                record_type = str(nsid)

                path_to_class = f'models.{get_import_path(nsid)}.{class_name}'

                type_conversion_lines.append(f"'{record_type}': {path_to_class},")
                unknown_record_type_hint_lines.append(f"{_(4)}'{path_to_class}',")
                unknown_record_type_pydantic_lines.append(f"{_(4)}'{path_to_class}',")

    type_conversion_lines.append('}')

    unknown_record_type_hint_lines.append(']')
    unknown_record_type_pydantic_lines.append('], Field(discriminator="py_type")]')
    unknown_record_type_pydantic_lines.append(
        "UnknownType: te.TypeAlias = t.Union[UnknownRecordTypePydantic, 'base.DotDictType']"
    )

    unknown_record_type_hint_lines.extend(unknown_record_type_pydantic_lines)

    write_code(_MODELS_OUTPUT_DIR.joinpath('type_conversion.py'), join_code(type_conversion_lines))
    write_code(_MODELS_OUTPUT_DIR.joinpath('unknown_type.py'), join_code(unknown_record_type_hint_lines))


def _generate_init_files(root_package_path: Path) -> None:
    # One of the ways that I tried. Doesn't work well due to circular imports
    for root, dirs, files in os.walk(root_package_path):
        root_path = Path(root)

        import_lines = []
        for dir_name in dirs:
            if dir_name.startswith('__'):
                continue

            import_parts = root_path.parts[root_path.joinpath(dir_name).parts.index(_MODELS_OUTPUT_DIR.parent.name) :]
            from_import = '.'.join(import_parts)

            if dir_name in {'app', 'com'}:
                continue

            import_lines.append(f'from {from_import} import {dir_name}')

        for file_name in files:
            if file_name.startswith('__'):
                continue

            import_parts = root_path.parts[root_path.parts.index(_MODELS_OUTPUT_DIR.parent.name) :]
            from_import = '.'.join(import_parts)

            import_lines.append(f'from atproto.{from_import} import {file_name[:-3]}')

        if root_path.name == 'models':
            # FIXME skip for now. should be generated too
            continue

        if root_path.name == '__pycache__':
            continue

        write_code(root_path.joinpath('__init__.py'), join_code(import_lines))


def _generate_empty_init_files(root_package_path: Path):
    for root, dirs, files in os.walk(root_package_path):
        root_path = Path(root)

        for dir_name in dirs:
            if dir_name.startswith('__'):
                continue

            if dir_name in {'app', 'com'}:
                continue

        for file_name in files:
            if file_name.startswith('__'):
                continue

        if root_path.name == 'models':
            # FIXME skip for now. should be generated too
            continue

        if root_path.name == '__pycache__':
            continue

        write_code(root_path.joinpath('__init__.py'), DISCLAIMER)


def _generate_import_aliases(root_package_path: Path) -> None:
    # is generates __init__.py file if models dir with aliases like this:
    # from xrpc_client.models.app.bsky.actor import defs as AppBskyActorDefs # noqa: ERA001

    import_lines = []
    ids_db = ['class _Ids:']
    for root, __, files in os.walk(root_package_path):
        root_path = Path(root)

        if root_path == root_package_path:
            continue

        for file in files:
            if file.startswith(('.', '__', '.pyc')):
                continue
            if '.cpython-' in file:
                continue

            import_parts = root_path.parts[root_path.parts.index(_MODELS_OUTPUT_DIR.parent.name) :]
            from_import = '.'.join(import_parts)

            nsid_parts = list(root_path.parts[root_path.parts.index('models') + 1 :])
            method_name_parts = file[:-3].split('_')
            alias_name = ''.join([p.capitalize() for p in [*nsid_parts, *method_name_parts]])

            camel_case_method_name = method_name_parts[0] + ''.join(ele.title() for ele in method_name_parts[1:])
            method_path = f"{'.'.join(nsid_parts)}.{camel_case_method_name}"
            ids_db.append(f"{_(1)}{alias_name}: str = '{method_path}'")

            import_lines.append(f'from atproto.{from_import} import {file[:-3]} as {alias_name}')

    import_lines.append(
        'from atproto.xrpc_client.models.utils import '
        'get_model_as_dict, '
        'get_model_as_json, '
        'get_or_create, '
        'is_record_type'
    )
    import_lines.append('from atproto.xrpc_client.models.models_loader import load_models')

    ids_db.append('ids = _Ids()')
    import_lines.extend(ids_db)

    import_lines.append('load_models()')

    write_code(_MODELS_OUTPUT_DIR.joinpath('__init__.py'), join_code(import_lines))


def generate_models(lexicon_dir: t.Optional[Path] = None, output_dir: t.Optional[Path] = None) -> None:
    if lexicon_dir:
        builder.lexicon_dir.set(lexicon_dir)

    if output_dir:
        # TODO(MarshalX): Temp hack for CLI. Pass output_dir everywhere.
        global _MODELS_OUTPUT_DIR
        _MODELS_OUTPUT_DIR = output_dir

    _generate_params_models(builder.build_params_models())
    _generate_data_models(builder.build_data_models())
    _generate_response_models(builder.build_response_models())
    _generate_def_models(builder.build_def_models())

    _generate_record_models(builder.build_record_models())
    _generate_record_type_database(builder.build_record_models())

    _generate_empty_init_files(_MODELS_OUTPUT_DIR)
    _generate_import_aliases(_MODELS_OUTPUT_DIR)

    format_code(_MODELS_OUTPUT_DIR)

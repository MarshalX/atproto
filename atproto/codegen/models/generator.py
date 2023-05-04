from enum import Enum
from pathlib import Path
from typing import Tuple, Union

from codegen import (
    INPUT_MODEL,
    OUTPUT_MODEL,
    PARAMS_MODEL,
    append_code,
    camel_case_split,
    capitalize_first_symbol,
    format_code,
)
from codegen import get_code_intent as _
from codegen import get_file_path_parts, get_import_path, join_code, write_code
from codegen.models import builder
from exceptions import InvalidNsidError
from lexicon import models
from nsid import NSID

_MODELS_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'models')


class ModelType(Enum):
    PARAMS = 'params'
    DATA = 'data'
    RESPONSE = 'response'
    DEF = 'def'
    RECORD = 'record'


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
    lines = [
        # isort formatted
        'from dataclasses import dataclass',
        # TODO(MarshalX): track and import only used hints? isort can't delete unused imports. mb add ruff
        'from typing import Any, List, Optional, Union, Type, TYPE_CHECKING',
        'from xrpc_client.models import base',
        'from xrpc_client.models.blob_ref import BlobRef',
        'from multiformats import CID',
        'from xrpc_client import models',
        '',
    ]

    return join_code(lines)


_NSID_WITH_IMPORTS = set()


def _save_code_import_if_not_exist(nsid) -> None:
    if nsid not in _NSID_WITH_IMPORTS:
        save_code(nsid, _get_model_imports())
        _NSID_WITH_IMPORTS.add(nsid)


def _get_model_class_def(name: str, model_type: ModelType) -> str:
    lines = ['@dataclass']

    if model_type is ModelType.PARAMS:
        lines.append(f'class {PARAMS_MODEL}(base.ParamsModelBase):')
    elif model_type is ModelType.DATA:
        lines.append(f'class {INPUT_MODEL}(base.DataModelBase):')
    elif model_type is ModelType.RESPONSE:
        lines.append(f'class {OUTPUT_MODEL}(base.ResponseModelBase):')
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


def _get_ref_typehint(nsid: NSID, field_type_def, main_def_name: str, *, optional: bool) -> str:
    model_path, _ = _resolve_nsid_ref(nsid, field_type_def.ref)
    return _get_optional_typehint(f"'{model_path}'", optional=optional)


def _resolve_nsid_ref(nsid: NSID, ref: str) -> Tuple[str, str]:
    """Returns path to the model and model name"""
    if '#' in ref:
        ref_nsid_str, def_name = ref.split('#', 1)
        try:
            ref_nsid = NSID.from_str(ref_nsid_str)
            return get_model_path(ref_nsid, def_name), def_name
        except InvalidNsidError:
            return get_model_path(nsid, def_name), def_name
    else:
        ref_nsid = NSID.from_str(ref)
        return get_model_path(nsid, ref_nsid.name), ref_nsid.name


def _get_ref_union_typehint(nsid: NSID, field_type_def, *, optional: bool) -> str:
    def_names = []
    for ref in field_type_def.refs:
        import_path, _ = _resolve_nsid_ref(nsid, ref)
        def_names.append(import_path)

    def_names = ', '.join([f"'{name}'" for name in def_names])
    return _get_optional_typehint(f"Union[{def_names}]", optional=optional)


def _get_model_field_typehint(
    nsid: NSID, field_name: str, field_type_def, *, optional: bool, def_name: str = None
) -> str:
    field_type = type(field_type_def)

    if field_type == models.LexUnknown:
        # TODO(MarshalX): it's record. think about could we add useful typehint
        return _get_optional_typehint('Any', optional=optional)

    type_hint = _LEXICON_TYPE_TO_PRIMITIVE_TYPEHINT.get(field_type)
    if type_hint:
        return _get_optional_typehint(type_hint, optional=optional)

    if field_type is models.LexArray:
        items_type_hint = _get_model_field_typehint(nsid, field_name, field_type_def.items, optional=False)
        return _get_optional_typehint(f'List[{items_type_hint}]', optional=optional)

    if field_type is models.LexRef:
        return _get_ref_typehint(nsid, field_type_def, def_name, optional=optional)

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


def _gen_description_by_camel_case_name(name: str):
    words = camel_case_split(name)
    words = [w.lower() for w in words]
    words[0] = words[0].capitalize()
    return ' '.join(words)


def _gen_description_by_nsid_or_camel_case_name(name: Union[str, NSID]) -> str:
    if isinstance(name, NSID):
        return f"{name.name} from {name.authority}"

    return _gen_description_by_camel_case_name(name)


def _get_model_docstring(
    nsid: Union[str, NSID], lex_object: Union[models.LexObject, models.LexXrpcParameters], model_type: ModelType
) -> str:
    model_desc = lex_object.description
    if model_desc is None:
        model_desc = _gen_description_by_nsid_or_camel_case_name(nsid)
    model_desc = f'{model_desc} for {model_type.value} type.'

    doc_string = [f'{_(1)}"""{model_desc}', '', f'{_(1)}Attributes:']

    for field_name, field_type in lex_object.properties.items():
        field_desc = field_type.description
        if field_desc is None:
            field_desc = _gen_description_by_camel_case_name(field_name)
        if field_desc[-1] not in {'.', '?', '!'}:
            field_desc += '.'

        doc_string.append(f'{_(2)}{field_name}: {field_desc}')

    doc_string.append(f'{_(1)}"""')
    doc_string.append('')

    return join_code(doc_string)


def _get_model(nsid: NSID, lex_object: Union[models.LexObject, models.LexXrpcParameters], def_name: str = None) -> str:
    required_fields = _get_req_fields_set(lex_object)

    fields = []
    optional_fields = []

    for field_name, field_type in lex_object.properties.items():
        is_optional = field_name not in required_fields
        type_hint = _get_model_field_typehint(nsid, field_name, field_type, optional=is_optional, def_name=def_name)

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
    ref_class, _ = _resolve_nsid_ref(nsid, ref.ref)
    # ref_class = _get_ref_class(nsid, ref, nsid.name)
    ref_typehint = f'Type[{ref_class}]'

    # "Ref" suffix required to fix name collisions from different namespaces
    return f'{OUTPUT_MODEL}Ref: {ref_typehint} = {ref_class}\n\n'


def _get_model_raw_data(name: str) -> str:
    return f'{name}: Union[Type[str], Type[bytes]] = bytes\n\n'


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
        elif isinstance(body.schema, models.LexRef):
            lines.append(_get_model_ref(nsid, body.schema))
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


def _generate_def_model(nsid: NSID, def_name: str, def_model: models.LexObject) -> str:
    lines = [
        _get_model_class_def(def_name, ModelType.DEF),
        _get_model_docstring(def_name, def_model, ModelType.DEF),
        _get_model(nsid, def_model, def_name),
    ]

    if def_name == 'main':
        lines.append(f"{_(1)}_type: str = '{nsid}'")

    lines.append('')

    return join_code(lines)


def _generate_def_token(def_name: str, def_model: models.LexToken) -> str:
    lines = [
        f"{get_def_model_name(def_name)} = '{def_name}'",
        # TODO(MarshalX): doesn't properly work. typing.Literal requires drop support of Python 3.7...
        '',
        '',
    ]
    return join_code(lines)


def _generate_def_string(def_name: str, def_model: models.LexString) -> str:
    # hardcoded. doesn't support all fields

    type_hint = ''

    if def_model.knownValues:
        # TODO use ref resolver
        known_values = ["'" + get_def_model_name(v.split('#', 1)[1]) + "'" for v in def_model.knownValues]
        known_values = ', '.join(known_values)

        # TODO(MarshalX): doesn't properly work. typing.Literal requires drop support of Python 3.7...
        type_hint = f': Union[{known_values}]'

    lines = [
        f"{get_def_model_name(def_name)}{type_hint} = '{def_name}'",
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
                save_code_part(nsid, _generate_def_token(def_name, def_model))
            if isinstance(def_model, models.LexString):
                save_code_part(nsid, _generate_def_string(def_name, def_model))
            if isinstance(def_model, models.LexObject):
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_model))


def _generate_record_models(lex_db: builder.LexDB) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            if isinstance(def_record, models.LexRecord):
                # TODO(MarshalX): Process somehow def_record.key?
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_record.record))


def generate_models():
    _generate_params_models(builder.build_params_models())
    _generate_data_models(builder.build_data_models())
    _generate_response_models(builder.build_response_models())
    _generate_def_models(builder.build_def_models())
    _generate_record_models(builder.build_record_models())

    format_code(_MODELS_OUTPUT_DIR)

    print('Done')


if __name__ == '__main__':
    generate_models()

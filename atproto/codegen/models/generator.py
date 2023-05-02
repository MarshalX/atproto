from enum import Enum
from pathlib import Path
from typing import Union

from codegen import capitalize_first_symbol, format_code
from codegen import get_code_intent as _
from codegen import join_code, write_code
from codegen.models import builder
from exceptions import InvalidNsidError
from lexicon import models
from nsid import NSID

_MODELS_OUTPUT_DIR = Path(__file__).parent.parent.parent.joinpath('xrpc_client', 'models')
_PARAMS_MODELS_FILENAME = 'params.py'
_DATA_MODELS_FILENAME = 'data.py'
_RESPONSE_MODELS_FILENAME = 'responses.py'
_DEFS_MODELS_FILENAME = 'defs.py'
_RECORDS_MODELS_FILENAME = 'records.py'


_PARAMS_SUFFIX = 'Params'
_INPUT_SUFFIX = 'Data'
_OPTIONS_SUFFIX = 'Options'
_OUTPUT_SUFFIX = 'Response'


class ModelType(Enum):
    PARAMS = 'params'
    DATA = 'data'
    OPTIONS = 'options'
    RESPONSE = 'response'
    DEF = 'def'
    RECORD = 'record'


def get_params_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_PARAMS_SUFFIX}'


def get_data_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_INPUT_SUFFIX}'


def get_options_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_OPTIONS_SUFFIX}'


def get_response_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}{_OUTPUT_SUFFIX}'


def get_def_model_name(method_name: str) -> str:
    return f'{capitalize_first_symbol(method_name)}'


def _get_model_imports(model_type: ModelType) -> str:
    model_imports = {
        model_type.PARAMS: 'ParamsModelBase',
        model_type.DATA: 'DataModelBase',
        model_type.OPTIONS: 'OptionsModelBase',
        model_type.RESPONSE: 'ResponseModelBase',
    }

    lines = [
        # isort formatted
        'from dataclasses import dataclass',
        # TODO(MarshalX): track and import only used hints? isort can't delete unused imports. mb add ruff
        'from typing import Any, List, Optional, Union, Type, TYPE_CHECKING',
    ]

    # TODO(MarshalX): Rewrite. not universal
    if model_type not in {ModelType.DEF, ModelType.RECORD}:
        lines.append('')
        lines.append(f"from xrpc_client.models.base import {model_imports.get(model_type)}")

    if model_type in {ModelType.DEF, ModelType.RECORD}:
        lines.append('from xrpc_client.models.blob_ref import BlobRef')
        lines.append('from multiformats import CID')
    if model_type is ModelType.RESPONSE:
        lines.append('from xrpc_client.models.defs import *')
    elif model_type in {ModelType.DATA, ModelType.RECORD}:
        lines.append('if TYPE_CHECKING:')
        lines.append(f'{_(1)}from xrpc_client.models.defs import *')
        lines.append('')

    return join_code(lines)


def _get_model_class_def(name: str, model_type: ModelType) -> str:
    lines = ['@dataclass']

    if model_type is ModelType.PARAMS:
        lines.append(f'class {get_params_model_name(name)}(ParamsModelBase):')
    elif model_type is ModelType.DATA:
        lines.append(f'class {get_data_model_name(name)}(DataModelBase):')
    elif model_type is ModelType.OPTIONS:
        lines.append(f'class {get_options_model_name(name)}(OptionsModelBase):')
    elif model_type is ModelType.RESPONSE:
        lines.append(f'class {get_response_model_name(name)}(ResponseModelBase):')
    elif model_type is ModelType.DEF:
        lines.append(f'class {get_def_model_name(name)}:')

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


def _get_ref_class(field_type_def, main_def_name: str) -> str:
    def_name = main_def_name

    if '#' in field_type_def.ref:
        def_name = field_type_def.ref.split('#', 1)[1]

    return get_def_model_name(def_name)


def _get_ref_typehint(field_type_def, main_def_name: str, *, optional: bool) -> str:
    def_name = main_def_name

    try:
        def_name = NSID.from_str(field_type_def.ref).name
    except InvalidNsidError:
        if '#' in field_type_def.ref:
            def_name = field_type_def.ref.split('#', 1)[1]

    def_name = get_def_model_name(def_name)
    return _get_optional_typehint(f"'{def_name}'", optional=optional)


def _get_ref_union_typehint(field_type_def, *, optional: bool) -> str:
    def_names = []
    for ref in field_type_def.refs:
        if '#' in ref:
            def_name = ref.split('#', 1)[1]
        else:
            def_name = NSID.from_str(ref).name
        def_names.append(get_def_model_name(def_name))

    def_names = ', '.join([f"'{name}'" for name in def_names])
    return _get_optional_typehint(f"Union[{def_names}]", optional=optional)


def _get_model_field_typehint(field_name: str, field_type_def, *, optional: bool, def_name: str = None) -> str:
    field_type = type(field_type_def)

    if field_type == models.LexUnknown:
        # TODO(MarshalX): it's record. think about could we add useful typehint
        return _get_optional_typehint('Any', optional=optional)

    type_hint = _LEXICON_TYPE_TO_PRIMITIVE_TYPEHINT.get(field_type)
    if type_hint:
        return _get_optional_typehint(type_hint, optional=optional)

    if field_type is models.LexArray:
        items_type_hint = _get_model_field_typehint(field_name, field_type_def.items, optional=False)
        return _get_optional_typehint(f'List[{items_type_hint}]', optional=optional)

    if field_type is models.LexRef:
        return _get_ref_typehint(field_type_def, def_name, optional=optional)

    if field_type is models.LexRefUnion:
        return _get_ref_union_typehint(field_type_def, optional=optional)

    if field_type is models.LexCidLink:
        return _get_optional_typehint(f'CID', optional=optional)

    if field_type is models.LexBytes:
        # CAR file containing relevant blocks
        return _get_optional_typehint('Union[str, bytes]', optional=optional)

    if field_type is models.LexBlob:
        # yes, it returns blob,but actually it's blob ref here
        return _get_optional_typehint('BlobRef', optional=optional)

    raise ValueError(f'Unknown field type {field_name.__name__}')


def _get_req_fields_set(lex_obj) -> set:
    required_fields = set()
    if lex_obj.required:
        required_fields = set(lex_obj.required)

    if hasattr(lex_obj, 'nullable') and lex_obj.nullable:
        # TODO(MarshalX): not 100% the same thing. think about it
        required_fields = required_fields.difference(set(lex_obj.nullable))

    return required_fields


def _get_model(properties: dict, required_fields: set, def_name: str = None) -> str:
    fields = []
    optional_fields = []

    for field_name, field_type in properties.items():
        is_optional = field_name not in required_fields
        type_hint = _get_model_field_typehint(field_name, field_type, optional=is_optional, def_name=def_name)

        field_def = f'{_(1)}{field_name}: {type_hint}'
        if is_optional:
            optional_fields.append(field_def)
        else:
            fields.append(field_def)

    optional_fields.sort()
    fields.sort()

    fields.extend(optional_fields)
    return join_code(fields)


def _get_model_object(def_name: str, lex_object: models.LexObject) -> str:
    return _get_model(lex_object.properties, _get_req_fields_set(lex_object), def_name=def_name)


def _get_model_parameters(parameters: models.LexXrpcParameters) -> str:
    return _get_model(parameters.properties, _get_req_fields_set(parameters))


def _get_model_schema(schema: models.LexObject) -> str:
    return _get_model(schema.properties, _get_req_fields_set(schema))


def _get_model_ref(name: str, ref: models.LexRef) -> str:
    ref_class = _get_ref_class(ref, name)
    ref_typehint = f'Type[{ref_class}]'

    # "Ref" suffix required to fix name collisions from different namespaces
    return f'{get_response_model_name(name)}Ref: {ref_typehint} = {ref_class}'


def _get_model_raw_data(name: str) -> str:
    return f'{name}: Union[Type[str], Type[bytes]] = bytes'


def _generate_params_model(nsid: NSID, definition: Union[models.LexXrpcProcedure, models.LexXrpcQuery]) -> str:
    lines = [_get_model_class_def(nsid.name, ModelType.PARAMS)]

    if definition.parameters:
        lines.append(_get_model_parameters(definition.parameters))

    return join_code(lines)


def _generate_xrpc_body_model(nsid: NSID, body: models.LexXrpcBody, model_type: ModelType) -> str:
    lines = []
    if body.schema:
        if isinstance(body.schema, models.LexObject):
            lines.append(_get_model_class_def(nsid.name, model_type))
            lines.append(_get_model_schema(body.schema))
        elif isinstance(body.schema, models.LexRef):
            lines.append(_get_model_ref(nsid.name, body.schema))
    else:
        if model_type is ModelType.DATA:
            model_name = get_data_model_name(nsid.name)
        elif model_type is ModelType.RESPONSE:
            model_name = get_response_model_name(nsid.name)
        else:
            raise ValueError('Wrong type or not implemented')

        lines.append(_get_model_raw_data(model_name))

    return join_code(lines)


def _generate_data_model(nsid: NSID, input_body: models.LexXrpcBody) -> str:
    return _generate_xrpc_body_model(nsid, input_body, ModelType.DATA)


def _generate_response_model(nsid: NSID, output_body: models.LexXrpcBody) -> str:
    return _generate_xrpc_body_model(nsid, output_body, ModelType.RESPONSE)


def _generate_def_model(def_name: str, def_model: models.LexObject) -> str:
    lines = [_get_model_class_def(def_name, ModelType.DEF), _get_model_object(def_name, def_model)]

    return join_code(lines)


def _generate_def_token(def_name: str, def_model: models.LexToken) -> str:
    lines = [
        f"{get_def_model_name(def_name)} = '{def_name}'",
        # TODO(MarshalX): doesn't properly work. typing.Literal requires drop support of Python 3.7...
    ]
    return join_code(lines)


def _generate_def_string(def_name: str, def_model: models.LexString) -> str:
    # hardcoded. doesn't support all fields

    type_hint = ''

    if def_model.knownValues:
        known_values = ["'" + get_def_model_name(v.split('#', 1)[1]) + "'" for v in def_model.knownValues]
        known_values = ', '.join(known_values)

        # TODO(MarshalX): doesn't properly work. typing.Literal requires drop support of Python 3.7...
        type_hint = f': Union[{known_values}]'

    lines = [
        f"{get_def_model_name(def_name)}{type_hint} = '{def_name}'",
    ]

    return join_code(lines)


def _generate_params_models(lex_db: builder.LexDB) -> None:
    lines = [_get_model_imports(ModelType.PARAMS)]

    for nsid, defs in lex_db.items():
        definition = defs['main']
        if definition.parameters:
            lines.append(_generate_params_model(nsid, definition))

    write_code(_MODELS_OUTPUT_DIR.joinpath(_PARAMS_MODELS_FILENAME), join_code(lines))
    format_code(_MODELS_OUTPUT_DIR.joinpath(_PARAMS_MODELS_FILENAME))


def _generate_data_models(lex_db: builder.LexDB) -> None:
    lines = [_get_model_imports(ModelType.DATA)]

    for nsid, defs in lex_db.items():
        definition = defs['main']
        if definition.input:
            lines.append(_generate_data_model(nsid, definition.input))

    write_code(_MODELS_OUTPUT_DIR.joinpath(_DATA_MODELS_FILENAME), join_code(lines))
    format_code(_MODELS_OUTPUT_DIR.joinpath(_DATA_MODELS_FILENAME))


def _generate_response_models(lex_db: builder.LexDB) -> None:
    lines = [_get_model_imports(ModelType.RESPONSE)]

    for nsid, defs in lex_db.items():
        definition = defs['main']
        if definition.output:
            lines.append(_generate_response_model(nsid, definition.output))

    write_code(_MODELS_OUTPUT_DIR.joinpath(_RESPONSE_MODELS_FILENAME), join_code(lines))
    format_code(_MODELS_OUTPUT_DIR.joinpath(_RESPONSE_MODELS_FILENAME))


def _generate_def_models(lex_db: builder.LexDB) -> None:
    lines = [_get_model_imports(ModelType.DEF)]

    for nsid, defs in lex_db.items():
        for def_name, def_model in defs.items():
            if isinstance(def_model, models.LexToken):
                lines.append(_generate_def_token(def_name, def_model))
            if isinstance(def_model, models.LexString):
                lines.append(_generate_def_string(def_name, def_model))
            if isinstance(def_model, models.LexObject):
                if def_name == 'main':
                    def_name = nsid.name

                lines.append(_generate_def_model(def_name, def_model))

    write_code(_MODELS_OUTPUT_DIR.joinpath(_DEFS_MODELS_FILENAME), join_code(lines))
    format_code(_MODELS_OUTPUT_DIR.joinpath(_DEFS_MODELS_FILENAME))


def _generate_record_models(lex_db: builder.LexDB) -> None:
    lines = [_get_model_imports(ModelType.RECORD)]

    for nsid, defs in lex_db.items():
        for def_name, def_record in defs.items():
            if isinstance(def_record, models.LexRecord):
                if def_name == 'main':
                    def_name = nsid.name

                # TODO(MarshalX): Process somehow def_record.key?
                lines.append(_generate_def_model(def_name, def_record.record))

    write_code(_MODELS_OUTPUT_DIR.joinpath(_RECORDS_MODELS_FILENAME), join_code(lines))
    format_code(_MODELS_OUTPUT_DIR.joinpath(_RECORDS_MODELS_FILENAME))


def generate_models():
    _generate_params_models(builder.build_params_models())
    _generate_data_models(builder.build_data_models())
    _generate_response_models(builder.build_response_models())
    _generate_def_models(builder.build_def_models())
    _generate_record_models(builder.build_record_models())
    print('Done')


if __name__ == '__main__':
    generate_models()

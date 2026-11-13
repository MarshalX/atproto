import keyword
import os
import typing as t
from enum import Enum
from functools import cache
from pathlib import Path

from atproto_core.exceptions import InvalidNsidError
from atproto_core.nsid import NSID
from atproto_lexicon import models
from atproto_lexicon.refs import find_unresolved_refs
from pydantic import alias_generators

from atproto_codegen.config import CodegenConfig, get_config, use_config
from atproto_codegen.consts import (
    DISCLAIMER,
    INPUT_DICT,
    INPUT_MODEL,
    OUTPUT_MODEL,
    PARAMS_DICT,
    PARAMS_MODEL,
)
from atproto_codegen.exceptions import UnresolvedReferenceError, UnsupportedLexiconError
from atproto_codegen.models import builder
from atproto_codegen.record_templates import (
    RECORD_CREATE_RESPONSE_MODEL_TEMPLATE,
    RECORD_GET_RESPONSE_MODEL_TEMPLATE,
    RECORD_LIST_RESPONSE_MODEL_TEMPLATE,
)
from atproto_codegen.utils import (
    append_code,
    camel_case_split,
    capitalize_first_symbol,
    convert_camel_case_to_snake_case,
    format_code,
    gen_description_by_camel_case_name,
    get_def_model_name,
    get_file_path_parts,
    get_import_path,
    get_module_path_parts,
    get_record_model_name,
    join_code,
    resolve_ref,
    to_docstring_text,
    to_identifier,
    to_one_line,
    to_pascal_case,
    write_code,
)
from atproto_codegen.utils import get_code_intent as _

# Mirror of models_loader._UTILS_EXPORTS. Duplicated (not imported) so that codegen never imports atproto_client,
# which would eagerly resolve generated models that may not exist yet during regeneration
_UTILS_EXPORTS = frozenset(
    {
        'create_strong_ref',
        'get_model_as_dict',
        'get_model_as_json',
        'get_or_create',
        'is_record_type',
    }
)


class ModelType(Enum):
    PARAMS = 'Parameters'
    DATA = 'Input data'
    RESPONSE = 'Output data'
    DEF = 'Definition'
    RECORD = 'Record'


class TypedDictType(Enum):
    PARAMS = 'Parameters'
    DATA = 'Input data'


def _model_path(nsid: NSID) -> Path:
    return get_config().models_output_dir.joinpath(*get_file_path_parts(nsid))


def save_code(nsid: NSID, code: str) -> None:
    write_code(_model_path(nsid), code)


def save_code_part(nsid: NSID, code: str) -> None:
    append_code(_model_path(nsid), code)


def _get_model_imports() -> str:
    config = get_config()
    base = f'{config.base_package}.models'

    # we are using ruff with F401 autofix to delete unused imports
    lines = [
        'import typing as t',
        '',
        'import typing_extensions as te',
        'from pydantic import Field',
        '',
        f'from {base} import bytes_type, string_formats',
        '',
        'if t.TYPE_CHECKING:',
        f'{_(1)}from {config.package} import models',
        f'{_(1)}from {base}.unknown_type import UnknownType',
        f'{_(1)}from {base}.unknown_type import UnknownInputType',
        f'{_(1)}from {base}.blob_ref import BlobRef',
        f'{_(1)}from atproto_core.cid import CIDType',
        f'from {base} import base',
        f'from {base} import unknown_union',
        '',
        '',
    ]

    return join_code(lines)


_nsid_with_imports: t.Set[NSID] = set()


def _save_code_import_if_not_exist(nsid: NSID) -> None:
    if nsid not in _nsid_with_imports:
        lines = [DISCLAIMER, _get_model_imports()]
        save_code(nsid, join_code(lines))
        _nsid_with_imports.add(nsid)


def _get_model_class_def(name: str, model_type: ModelType) -> str:
    lines: t.List[str] = []

    if model_type is ModelType.PARAMS:
        lines.append(f'class {PARAMS_MODEL}(base.ParamsModelBase):')
    elif model_type is ModelType.DATA:
        lines.append(f'class {INPUT_MODEL}(base.DataModelBase):')
    elif model_type is ModelType.RESPONSE:
        lines.append(f'class {OUTPUT_MODEL}(base.ResponseModelBase):')
    elif model_type is ModelType.RECORD:
        lines.append(f'class {get_record_model_name(name)}(base.RecordModelBase):')
    elif model_type is ModelType.DEF:
        lines.append(f'class {get_def_model_name(name)}(base.ModelBase):')

    lines.append('')

    return join_code(lines)


def _get_typeddict_class_def(name: str, model_type: TypedDictType) -> str:
    lines: t.List[str] = []

    if model_type is TypedDictType.PARAMS:
        lines.append(f'class {PARAMS_DICT}(t.TypedDict):')
    elif model_type is TypedDictType.DATA:
        lines.append(f'class {INPUT_DICT}(t.TypedDict):')

    lines.append('')

    return join_code(lines)


#: Lexicon types a model field can have
_FieldTypeDef = t.Union[models.LexPrimitive, models.LexArray, models.LexBlob, models.LexObject]


def _get_optional_typehint(type_hint: str, *, optional: bool) -> str:
    if optional:
        return f't.Optional[{type_hint}]'
    return type_hint


def _resolve_token_ref(nsid: NSID, value: str) -> t.Optional[str]:
    """Return the model path of the token a string value names, or :obj:`None` for a plain string."""
    if '#' not in value:
        return None

    ref_nsid_str, def_name = value.split('#', 1)
    try:
        ref_nsid = NSID.from_str(ref_nsid_str) if ref_nsid_str else nsid
    except InvalidNsidError:
        return None

    model_name = get_def_model_name(def_name)
    if not builder.is_token(ref_nsid, def_name, get_import_path(ref_nsid), model_name):
        return None

    return f'models.{get_import_path(ref_nsid)}.{model_name}'


def _get_str_enum_typehint(nsid: NSID, field_type_def: models.LexString, *, optional: bool) -> str:
    values = field_type_def.known_values or field_type_def.enum or []

    union_type_parts = []
    literals = []
    literals_index = None
    for value in values:
        token_path = _resolve_token_ref(nsid, value)
        if token_path:
            union_type_parts.append(f"'{token_path}'")
        else:
            # literal; all of them are merged into a single multi-member t.Literal
            if literals_index is None:
                literals_index = len(union_type_parts)
                union_type_parts.append('')
            literals.append(repr(value))

    if literals_index is not None:
        union_type_parts[literals_index] = f't.Literal[{", ".join(literals)}]'

    # known_values is not closed enum
    if not field_type_def.enum:
        union_type_parts.append('str')

    if len(union_type_parts) == 1:
        # t.Union of a single member is invalid for type checkers
        return union_type_parts[0]

    return f't.Union[{", ".join(union_type_parts)}]'


def _get_str_typehint(nsid: NSID, field_type_def: models.LexString, *, optional: bool) -> str:
    if field_type_def.const is not None:
        return _get_optional_typehint(f't.Literal[{field_type_def.const!r}]', optional=optional)

    str_typehint = 'str'

    # Map lexicon string formats to our validator types
    if field_type_def.format:
        # Map format types to our string_formats types
        format_map = {
            'at-identifier': 'string_formats.AtIdentifier',
            'at-uri': 'string_formats.AtUri',
            'cid': 'string_formats.Cid',
            'datetime': 'string_formats.DateTime',
            'did': 'string_formats.Did',
            'handle': 'string_formats.Handle',
            'nsid': 'string_formats.Nsid',
            'tid': 'string_formats.Tid',
            'record-key': 'string_formats.RecordKey',
            'uri': 'string_formats.Uri',
            'language': 'string_formats.Language',
        }
        str_typehint = format_map.get(field_type_def.format, 'str')

    # Handle existing enum/known_values logic
    if field_type_def.known_values or field_type_def.enum:
        str_typehint = _get_str_enum_typehint(nsid, field_type_def, optional=optional)

    return _get_optional_typehint(str_typehint, optional=optional)


def _get_unknown_typehint(*, optional: bool, is_input_type: bool) -> str:
    return _get_optional_typehint("'UnknownInputType'" if is_input_type else "'UnknownType'", optional=optional)


def _get_ref_typehint(nsid: NSID, field_type_def: models.LexRef, *, optional: bool, is_input_type: bool) -> str:
    model_path = resolve_ref(nsid, field_type_def.ref)
    if model_path is None:
        return _get_unknown_typehint(optional=optional, is_input_type=is_input_type)

    return _get_optional_typehint(f"'{model_path}'", optional=optional)


def _get_ref_union_typehint(nsid: NSID, field_type_def: models.LexRefUnion, *, optional: bool) -> str:
    model_paths = [resolve_ref(nsid, ref) for ref in field_type_def.refs]
    def_names = [model_path for model_path in model_paths if model_path is not None]
    # a union that lost members must accept the types it can no longer name
    is_closed = bool(field_type_def.closed) and len(def_names) == len(model_paths)

    if not model_paths and field_type_def.closed:
        raise ValueError('The schema is invalid because union must have at least one type when it is closed')

    is_unknown_union = not def_names

    if is_unknown_union:
        # union of unknown types but it must have $type field.
        def_names.append('base.UnknownUnionModel')

    # an open union may carry a $type this SDK release doesn't know yet; OpenUnion adds the DotDict
    # fallback so such members don't fail the whole response. ref: https://github.com/MarshalX/atproto/issues/354
    members = _union_typehint([f"'{name}'" for name in def_names])
    if not is_unknown_union and not is_closed:
        return _get_optional_typehint(f'unknown_union.OpenUnion[{members}]', optional=optional)

    # For discriminated unions, optionality is handled by Optional[] wrapper, not Field(default=None)
    # Pydantic 2.12.3+ warns that default=None has no effect in union context
    # Unknown unions can't use discriminator because $type is unknown
    def_field_meta = 'Field()' if is_unknown_union else 'Field(discriminator="py_type")'

    annotated_union = f'te.Annotated[{members}, {def_field_meta}]'
    return _get_optional_typehint(annotated_union, optional=optional)


def _get_model_field_typehint(  # noqa: C901
    nsid: NSID,
    field_type_def: _FieldTypeDef,
    *,
    optional: bool,
    is_input_type: bool = False,
    inline_name: t.Optional[str] = None,
) -> str:
    if isinstance(field_type_def, models.LexObject):
        if inline_name is None:
            raise ValueError('Inline object is not supported here')
        model_path = _register_inline_model(nsid, inline_name, field_type_def, is_input_type=is_input_type)
        return _get_optional_typehint(f"'{model_path}'", optional=optional)

    if isinstance(field_type_def, models.LexUnknown):
        # unknown type is a generic response with records or any not described type in the lexicon. for example, didDoc
        return _get_unknown_typehint(optional=optional, is_input_type=is_input_type)

    if isinstance(field_type_def, models.LexInteger):
        if field_type_def.const is not None:
            return _get_optional_typehint(f't.Literal[{field_type_def.const!r}]', optional=optional)
        return _get_optional_typehint('int', optional=optional)

    if isinstance(field_type_def, models.LexBoolean):
        return _get_optional_typehint('bool', optional=optional)

    if isinstance(field_type_def, models.LexString):
        return _get_str_typehint(nsid, field_type_def, optional=optional)

    if isinstance(field_type_def, models.LexArray):
        items_type_hint = _get_model_field_typehint(
            nsid,
            field_type_def.items,
            optional=False,
            is_input_type=is_input_type,
            inline_name=f'{inline_name}{_INLINE_ITEM_SUFFIX}' if inline_name else None,
        )
        items_constraints_field = _get_constraints_field(field_type_def.items)
        if items_constraints_field:
            items_type_hint = f'te.Annotated[{items_type_hint}, {items_constraints_field}]'
        return _get_optional_typehint(f't.List[{items_type_hint}]', optional=optional)

    if isinstance(field_type_def, models.LexRef):
        return _get_ref_typehint(nsid, field_type_def, optional=optional, is_input_type=is_input_type)

    if isinstance(field_type_def, models.LexRefUnion):
        return _get_ref_union_typehint(nsid, field_type_def, optional=optional)

    if isinstance(field_type_def, models.LexCidLink):
        return _get_optional_typehint("'CIDType'", optional=optional)

    if isinstance(field_type_def, models.LexBytes):
        return _get_optional_typehint('bytes_type.BytesType', optional=optional)

    if isinstance(field_type_def, models.LexBlob):
        # yes, it returns blob,but actually it's blob ref here
        return _get_optional_typehint("'BlobRef'", optional=optional)

    raise ValueError(f'Unknown field type {type(field_type_def).__name__}')


def _get_type_constraints(field_type_def: _FieldTypeDef) -> t.Dict[str, t.Any]:
    """Pydantic constraints implied by the type itself (not by default, const, or alias)."""
    constraints: t.Dict[str, t.Any] = {}

    if isinstance(field_type_def, (models.LexString, models.LexArray)):
        if field_type_def.min_length is not None:
            constraints['min_length'] = field_type_def.min_length
        if field_type_def.max_length is not None:
            constraints['max_length'] = field_type_def.max_length

    elif isinstance(field_type_def, models.LexInteger):
        if field_type_def.minimum is not None:
            constraints['ge'] = field_type_def.minimum
        if field_type_def.maximum is not None:
            constraints['le'] = field_type_def.maximum

    return constraints


def _get_field_code(field_params: t.Dict[str, t.Any]) -> str:
    """Generate the Field call from the pydantic field params."""
    params = ', '.join(f'{name}={value!r}' for name, value in field_params.items())
    return f'Field({params})'


def _get_constraints_field(field_type_def: _FieldTypeDef) -> str:
    """Generate the Field with constraints of the type itself. Empty string if there are no constraints."""
    constraints = _get_type_constraints(field_type_def)
    if not constraints:
        return ''

    return _get_field_code(constraints)


def _get_alias_params(alias_name: str) -> t.Dict[str, t.Any]:
    """Field params that pin a field to a property name the alias generator would not produce.

    Not ``alias``: type checkers would then require the alias as the constructor argument name.
    """
    # priority 2 keeps the alias generator of the base model from overriding them
    return {'validation_alias': alias_name, 'serialization_alias': alias_name, 'alias_priority': 2}


def _get_model_field_value(
    field_type_def: _FieldTypeDef,
    alias_name: t.Optional[str] = None,
    *,
    optional: bool,
) -> t.Dict[str, t.Any]:
    """Generate field value and metadata.

    Returns a dict with:
        - 'value': the field value (e.g., 'None' or 'Field(...)')
        - 'needs_annotated': whether this field needs Annotated wrapper
    """
    not_set = object()

    default: object = not_set
    frozen: object = not_set

    # Ref and RefUnion types handle their own Field generation in the type hint
    if isinstance(field_type_def, (models.LexRef, models.LexRefUnion)):
        if alias_name:
            return {'value': _get_field_code(_get_alias_params(alias_name)), 'needs_annotated': True}
        return {'value': '', 'needs_annotated': False}

    if isinstance(field_type_def, (models.LexInteger, models.LexString, models.LexBoolean)):
        if field_type_def.default is not None:
            default = field_type_def.default
        if field_type_def.const is not None:
            frozen = True

    if default is not_set and optional:
        default = None

    field_params = {
        'default': default,
        **(_get_alias_params(alias_name) if alias_name else {}),
        **_get_type_constraints(field_type_def),
        'frozen': frozen,
    }

    field_params = {name: value for name, value in field_params.items() if value is not not_set}
    non_default_params = {name: value for name, value in field_params.items() if name != 'default'}

    if not non_default_params:
        if 'default' not in field_params:
            return {'value': '', 'needs_annotated': False}

        # simple assignment instead of Field
        return {'value': repr(field_params['default']), 'needs_annotated': False}

    if optional:
        # for optional fields with constraints, exclude default from Field to avoid pydantic warning.
        # the Annotated pattern is used instead
        field_params.pop('default', None)

    return {'value': _get_field_code(field_params), 'needs_annotated': optional}


def _get_req_fields_set(lex_obj: t.Union[models.LexObject, models.LexXrpcParameters]) -> t.Set[str]:
    required_fields: t.Set[str] = set()
    if lex_obj.required:
        required_fields = set(lex_obj.required)

    if hasattr(lex_obj, 'nullable') and lex_obj.nullable:
        # TODO(MarshalX): not 100% the same thing. think about it
        required_fields = required_fields.difference(set(lex_obj.nullable))

    return required_fields


def _add_dot_to_end_if_not_exist(description: str) -> str:
    if description[-1] not in {'.', '?', '!'}:
        description += '.'
    return description


def _get_def_comment(name: str, description: t.Optional[str]) -> str:
    """Return the one-line description of a definition, made up from its name if it has none."""
    description = to_one_line(description or '')
    return description or gen_description_by_camel_case_name(name)


def _get_field_docstring(field_name: str, field_type: _FieldTypeDef) -> str:
    field_desc = capitalize_first_symbol(_get_def_comment(field_name, field_type.description))

    if isinstance(field_type, models.LexArray) and field_type.items.description:
        items_desc = capitalize_first_symbol(to_one_line(field_type.items.description))
        if items_desc:
            field_desc = f'{_add_dot_to_end_if_not_exist(field_desc)} {items_desc}'

    return _add_dot_to_end_if_not_exist(field_desc)


def _get_model_docstring(
    nsid: t.Union[str, NSID],
    lex_object: t.Union[models.LexXrpcQuery, models.LexSubscription, models.LexObject, models.LexXrpcParameters],
    model_type: ModelType,
) -> str:
    description = to_docstring_text(lex_object.description or '')
    model_desc = f' {description}' if description else ''
    model_desc = f'{model_type.value} model for :obj:`{nsid}`.{model_desc}'
    model_desc = _add_dot_to_end_if_not_exist(model_desc)

    doc_string = [f'{_(1)}"""{model_desc}"""', '']

    return join_code(doc_string)


@cache
def _get_pydantic_reserved_names() -> t.Set[str]:
    from pydantic import BaseModel

    class Model(BaseModel):
        pass

    instance = Model()

    return {name for name in dir(instance) if not name.startswith('_')}


def _get_python_reserved_names() -> t.Sequence[str]:
    return keyword.kwlist


#: Names the generated modules import. A field of the same name would shadow them in the class body.
_MODULE_RESERVED_NAMES = frozenset({'base', 'bytes_type', 'models', 'string_formats', 't', 'te', 'unknown_union'})

_TYPE_PROPERTY = '$type'
_FIELD_PREFIX = 'field'


def _is_reserved_variable_name(name: str) -> bool:
    return (
        name in _get_pydantic_reserved_names() or name in _get_python_reserved_names() or name in _MODULE_RESERVED_NAMES
    )


def _get_field_name(property_name: str) -> str:
    """Return the attribute name a lexicon property is generated as."""
    name = to_identifier(convert_camel_case_to_snake_case(property_name)).rstrip('_')
    if not name or name.startswith('_'):
        # a leading underscore makes a private attribute out of a pydantic field
        name = f'{_FIELD_PREFIX}{name}'
    if _is_reserved_variable_name(name):
        name += '_'

    return name


def _get_field_alias(field_name: str, property_name: str) -> t.Optional[str]:
    """Return the property name if the alias generator of the base model would not restore it."""
    if alias_generators.to_camel(field_name).removesuffix('_') == property_name:
        return None

    return property_name


def _iter_properties(
    lex_object: t.Union[models.LexObject, models.LexXrpcParameters],
) -> t.Iterator[t.Tuple[str, str, _FieldTypeDef]]:
    """Yield the property name, the field name and the type of every field to generate."""
    for property_name, field_type_def in lex_object.properties.items():
        # the type discriminator is a field of the model already
        if property_name != _TYPE_PROPERTY:
            yield property_name, _get_field_name(property_name), field_type_def


def _get_model(
    nsid: NSID,
    lex_object: t.Union[models.LexObject, models.LexXrpcParameters],
    owner: str,
    *,
    is_input_type: bool = False,
) -> str:
    required_fields = _get_req_fields_set(lex_object)

    fields = []
    optional_fields = []

    for property_name, field_name, field_type_def in _iter_properties(lex_object):
        is_optional = property_name not in required_fields

        type_hint = _get_model_field_typehint(
            nsid,
            field_type_def,
            optional=is_optional,
            is_input_type=is_input_type,
            inline_name=_get_inline_name(owner, property_name),
        )
        alias_name = _get_field_alias(field_name, property_name)
        field_value_info = _get_model_field_value(field_type_def, alias_name, optional=is_optional)
        description = _get_field_docstring(property_name, field_type_def)

        # Handle Annotated pattern for fields whose Field can not be the assigned value
        if field_value_info['needs_annotated']:
            # Wrap type in Annotated and add Field metadata
            type_hint = f'te.Annotated[{type_hint}, {field_value_info["value"]}]'
            value_def = ' = None' if is_optional else ''
        else:
            # Simple assignment
            if field_value_info['value']:
                value_def = f' = {field_value_info["value"]}'
            elif is_optional:
                # Optional fields without Field constraints still need = None
                value_def = ' = None'
            else:
                value_def = ''

        field_def = f'{_(1)}{field_name}: {type_hint}{value_def} #: {description}'

        if is_optional:
            optional_fields.append(field_def)
        else:
            fields.append(field_def)

    optional_fields.sort()
    fields.sort()

    fields.extend(optional_fields)

    fields.append('')

    return join_code(fields)


def _get_typeddict(
    nsid: NSID,
    lex_object: t.Union[models.LexObject, models.LexXrpcParameters],
    owner: str,
    *,
    is_input_type: bool = False,
) -> str:
    required_fields = _get_req_fields_set(lex_object)

    fields: t.List[str] = []
    optional_fields: t.List[str] = []

    for property_name, field_name, field_type_def in _iter_properties(lex_object):
        is_optional = property_name not in required_fields

        type_hint = _get_model_field_typehint(
            nsid,
            field_type_def,
            optional=is_optional,
            is_input_type=is_input_type,
            inline_name=_get_inline_name(owner, property_name),
        )
        description = _get_field_docstring(property_name, field_type_def)

        # Allow optional params to actually be omitted from the dict entirely
        type_hint_defaulting = f'te.NotRequired[{type_hint}]' if is_optional else type_hint
        field_def = f'{_(1)}{field_name}: {type_hint_defaulting} #: {description}'

        if is_optional:
            optional_fields.append(field_def)
        else:
            fields.append(field_def)

    optional_fields.sort()
    fields.sort()

    fields.extend(optional_fields)

    if len(fields) == 0:
        fields.append(f'{_(1)}pass')

    fields.append('')

    return join_code(fields)


class _InlineModel(t.NamedTuple):
    """Object declared in place of a property type, generated as a model of its own."""

    name: str
    lex_object: models.LexObject
    is_input_type: bool


_INLINE_ITEM_SUFFIX = 'Item'
_INLINE_NAME_SUFFIX = 'Object'
#: Class names every generated module may define besides the ones of its lexicon.
_MODULE_CLASS_NAMES = frozenset(
    {
        PARAMS_MODEL,
        PARAMS_DICT,
        INPUT_MODEL,
        INPUT_DICT,
        OUTPUT_MODEL,
        get_record_model_name(),
        'GetRecordResponse',
        'ListRecordsResponse',
        'CreateRecordResponse',
    }
)

#: Inline models of each lexicon by the name they were requested under.
_inline_models: t.Dict[NSID, t.Dict[str, _InlineModel]] = {}
_pending_inline_models: t.List[t.Tuple[NSID, _InlineModel]] = []


def _get_inline_name(owner: str, property_name: str) -> str:
    return f'{owner}{to_pascal_case(camel_case_split(property_name))}'


def _register_inline_model(
    nsid: NSID, requested_name: str, lex_object: models.LexObject, *, is_input_type: bool
) -> str:
    """Queue an inline object for generation and return the path to its model."""
    registered = _inline_models.setdefault(nsid, {})
    if requested_name not in registered:
        taken = {model.name for model in registered.values()} | _MODULE_CLASS_NAMES
        taken.update(get_def_model_name(def_name) for def_name in builder.get_defs(nsid))

        name = requested_name
        attempt = 1
        while name in taken:
            name = f'{requested_name}{_INLINE_NAME_SUFFIX}{attempt if attempt > 1 else ""}'
            attempt += 1

        registered[requested_name] = _InlineModel(name, lex_object, is_input_type)
        _pending_inline_models.append((nsid, registered[requested_name]))

    return f'models.{get_import_path(nsid)}.{registered[requested_name].name}'


def _generate_inline_models() -> None:
    # generating a model may queue the inline objects nested in it
    while _pending_inline_models:
        nsid, model = _pending_inline_models.pop(0)
        lines = [
            f'class {model.name}(base.ModelBase):',
            '',
            _get_model_docstring(nsid, model.lex_object, ModelType.DEF),
            _get_model(nsid, model.lex_object, model.name, is_input_type=model.is_input_type),
        ]
        save_code_part(nsid, join_code(lines))


def _get_model_raw_data(name: str) -> str:
    lines = [f'#: {name} raw data type.', f'{name}: te.TypeAlias = bytes\n\n']
    return join_code(lines)


def _generate_params_model(
    nsid: NSID, definition: t.Union[models.LexXrpcQuery, models.LexXrpcProcedure, models.LexSubscription]
) -> str:
    lines = [_get_model_class_def(nsid.name, ModelType.PARAMS)]

    if definition.parameters:
        lines.append(_get_model_docstring(nsid, definition.parameters, ModelType.PARAMS))
        lines.append(_get_model(nsid, definition.parameters, PARAMS_MODEL, is_input_type=True))

    lines.append(_get_typeddict_class_def(nsid.name, TypedDictType.PARAMS))

    if definition.parameters:
        lines.append(_get_typeddict(nsid, definition.parameters, PARAMS_MODEL, is_input_type=True))

    return join_code(lines)


def _generate_xrpc_body_model(nsid: NSID, body: models.LexXrpcBody, model_type: ModelType) -> str:
    lines = []
    if body.schema_:
        if isinstance(body.schema_, models.LexObject):
            lines.append(_get_model_class_def(nsid.name, model_type))
            lines.append(_get_model_docstring(nsid, body.schema_, model_type))
            is_input_type = model_type is ModelType.DATA
            owner = INPUT_MODEL if is_input_type else OUTPUT_MODEL
            lines.append(_get_model(nsid, body.schema_, owner, is_input_type=is_input_type))
        elif isinstance(body.schema_, models.LexRef):
            resolve_ref(nsid, body.schema_.ref)

            # here we can generate input and output model alises from the reference
            # but instead we just resolve reference inplace without intermediate model
            # maybe we will want to generate aliases in the future
            # so I leave this code here: https://github.com/MarshalX/atproto/pull/412
        elif not get_config().skip_invalid:
            raise UnsupportedLexiconError(f"'{nsid}' has a union as its body, which is not supported yet")
    else:
        if model_type is ModelType.DATA:
            model_name = INPUT_MODEL
        elif model_type is ModelType.RESPONSE:
            model_name = OUTPUT_MODEL
        else:
            raise ValueError('Wrong type or not implemented')

        lines.append(_get_model_raw_data(model_name))

    return join_code(lines)


def _generate_data_typedict(nsid: NSID, body: models.LexXrpcBody) -> str:
    lines: t.List[str] = []
    if isinstance(body.schema_, models.LexObject):
        lines.append(_get_typeddict_class_def(nsid.name, TypedDictType.DATA))
        lines.append(_get_typeddict(nsid, body.schema_, INPUT_MODEL, is_input_type=True))
    return join_code(lines)


def _generate_data_model(nsid: NSID, input_body: models.LexXrpcBody) -> str:
    return join_code(
        [_generate_xrpc_body_model(nsid, input_body, ModelType.DATA), _generate_data_typedict(nsid, input_body)]
    )


def _get_page_items_field(
    definition: t.Union[models.LexXrpcQuery, models.LexXrpcProcedure],
) -> t.Optional[t.Tuple[models.LexObject, str, models.LexArray]]:
    """Return the output schema and the array field holding page items if the query is cursor-paginated."""
    if not isinstance(definition, models.LexXrpcQuery) or not definition.parameters or not definition.output:
        return None

    schema = definition.output.schema_
    if not isinstance(schema, models.LexObject):
        return None
    if 'cursor' not in definition.parameters.properties or 'cursor' not in schema.properties:
        return None

    arrays = [(name, field) for name, field in schema.properties.items() if isinstance(field, models.LexArray)]
    if len(arrays) > 1:
        # extra arrays are side data (e.g. relatedProfiles); the page items are the required one
        arrays = [(name, field) for name, field in arrays if name in _get_req_fields_set(schema)]

    if len(arrays) != 1:
        return None

    name, field = arrays[0]
    return schema, name, field


def _generate_page_items_method(nsid: NSID, definition: t.Union[models.LexXrpcQuery, models.LexXrpcProcedure]) -> str:
    page_items_field = _get_page_items_field(definition)
    if page_items_field is None:
        return ''

    schema, field_name, field = page_items_field
    inline_name = _get_inline_name(OUTPUT_MODEL, field_name)
    type_hint = _get_model_field_typehint(nsid, field, optional=False, inline_name=inline_name)

    attr_name = _get_field_name(field_name)

    value = f'self.{attr_name}'
    if field_name not in _get_req_fields_set(schema):
        value = f'{value} or []'

    lines = [
        f'{_(1)}def get_page_items(self) -> {type_hint}:',
        f'{_(2)}"""Get the items of this page."""',
        f'{_(2)}return {value}',
        '',
    ]

    return join_code(lines)


def _generate_response_model(nsid: NSID, output_body: models.LexXrpcBody) -> str:
    return _generate_xrpc_body_model(nsid, output_body, ModelType.RESPONSE)


def _generate_def_model(nsid: NSID, def_name: str, def_model: models.LexObject, model_type: ModelType) -> str:
    owner = get_record_model_name() if model_type is ModelType.RECORD else get_def_model_name(def_name)
    lines = [
        _get_model_class_def(def_name, model_type),
        _get_model_docstring(nsid, def_model, model_type),
        _get_model(nsid, def_model, owner),
    ]

    def_type = f'{nsid}#{def_name}'
    if def_name == 'main':
        def_type = str(nsid)

    lines.append(f"{_(1)}py_type: t.Literal[{def_type!r}] = Field(default={def_type!r}, alias='$type', frozen=True)")
    lines.append('')

    return join_code(lines)


def _generate_def_token(nsid: NSID, def_name: str, def_model: models.LexToken) -> str:
    description = _get_def_comment(def_name, def_model.description)
    token = f'{nsid}#{def_name}'

    lines = [
        f'{get_def_model_name(def_name)} = t.Literal[{token!r}] #: {description}',
        '',
        '',
    ]
    return join_code(lines)


_AliasDef = t.Union[
    models.LexArray,
    models.LexBlob,
    models.LexBoolean,
    models.LexBytes,
    models.LexCidLink,
    models.LexInteger,
    models.LexString,
]


def _generate_def_alias(nsid: NSID, def_name: str, def_model: _AliasDef) -> str:
    """Generate a type alias for a definition that is not a model."""
    name = get_def_model_name(def_name)
    type_hint = _get_model_field_typehint(nsid, def_model, optional=False, inline_name=name)

    constraints_field = _get_constraints_field(def_model)
    if constraints_field:
        type_hint = f'te.Annotated[{type_hint}, {constraints_field}]'

    if isinstance(def_model, models.LexArray):
        return f'{name} = {type_hint}\n'

    lines = [
        f'{name} = {type_hint} #: {_get_def_comment(def_name, def_model.description)}',
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
            response_model = _generate_response_model(nsid, definition.output)
            save_code_part(nsid, join_code([response_model, _generate_page_items_method(nsid, definition)]))


def _generate_def_models(lex_db: builder.BuiltDefModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_model in defs.items():
            if isinstance(def_model, models.LexToken):
                save_code_part(nsid, _generate_def_token(nsid, def_name, def_model))
            elif isinstance(def_model, models.LexObject):
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_model, ModelType.DEF))
            elif isinstance(def_model, t.get_args(_AliasDef)):
                save_code_part(nsid, _generate_def_alias(nsid, def_name, def_model))
            else:
                # TRY004 is suppressed: this is an invalid lexicon schema, not a Python type
                # error; the rest of the generator reports such cases as ValueError too
                raise ValueError(f'Unhandled type {type(def_model)}')  # noqa: TRY004


def _generate_record_sugar_models(nsid: NSID) -> str:
    lines = []
    for model in [
        RECORD_GET_RESPONSE_MODEL_TEMPLATE,
        RECORD_LIST_RESPONSE_MODEL_TEMPLATE,
        RECORD_CREATE_RESPONSE_MODEL_TEMPLATE,
    ]:
        lines.append(model.format(record_import=get_import_path(nsid)))

    return join_code(lines)


def _generate_record_models(lex_db: builder.BuiltRecordModels) -> None:
    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            if isinstance(def_record, models.LexRecord):
                # TODO(MarshalX): Process somehow def_record.key?
                save_code_part(nsid, _generate_def_model(nsid, def_name, def_record.record, ModelType.RECORD))
                save_code_part(nsid, _generate_record_sugar_models(nsid))


def _union_typehint(members: t.List[str]) -> str:
    # t.Union of a single member is invalid for type checkers
    if not members:
        return 't.Any'
    if len(members) == 1:
        return members[0]
    return f't.Union[{", ".join(members)}]'


def _generate_record_type_database(lex_db: builder.BuiltRecordModels) -> None:
    config = get_config()
    base = f'{config.base_package}.models'

    type_conversion_lines = [
        f'from {base}.record_registry import RECORD_TYPE_TO_MODEL_CLASS',
        f'from {base}.record_registry import register_record_types',
        "__all__ = ['RECORD_TYPE_TO_MODEL_CLASS', 'RECORD_TYPES']",
        'RECORD_TYPES = {',
    ]

    import_lines = [
        'import typing as t',
        'import typing_extensions as te',
        f'from {base} import unknown_union',
        'if t.TYPE_CHECKING:',
        f'{_(4)}from {base} import base',
        f'{_(4)}from {config.package} import models',
        f'{_(4)}from {base} import dot_dict',
    ]
    unknown_record_type_members: t.List[str] = []
    if not config.is_self_gen:
        # records of the base package are resolved at runtime too, so its union is a member of ours
        import_lines.append(f'{_(4)}from {base} import unknown_type as base_unknown_type')
        unknown_record_type_members.append("'base_unknown_type.UnknownRecordType'")
    import_lines.append('')

    for nsid, defs in lex_db.items():
        _save_code_import_if_not_exist(nsid)

        for def_name, def_record in defs.items():
            # for now, there are records only in under "main" definition name.
            # need to rework a bit if this behavior is changed
            if isinstance(def_record, models.LexRecord):
                class_name = get_record_model_name(def_name)
                record_type = str(nsid)

                path_to_class = f'models.{get_import_path(nsid)}.{class_name}'

                type_conversion_lines.append(f"'{record_type}': '{get_import_path(nsid)}',")

                unknown_record_type_members.append(f"'{path_to_class}'")

    type_conversion_lines.append('}')
    type_conversion_lines.append(f"register_record_types('{config.models_package}', RECORD_TYPES)")

    unknown_record_type_hint_lines = [
        f'UnknownRecordType: te.TypeAlias = {_union_typehint(unknown_record_type_members)}'
    ]

    # the runtime type is deliberately open: records are resolved through the registry, so a package
    # generated from custom lexicons is decoded here too. UnknownRecordType stays for type checkers.
    unknown_type_lines = [
        *import_lines,
        *unknown_record_type_hint_lines,
        'if t.TYPE_CHECKING:',
        f'{_(1)}UnknownType: te.TypeAlias = te.Annotated[',
        f"{_(2)}t.Union[UnknownRecordType, 'dot_dict.DotDictType'], unknown_union.UnknownRecordFallback",
        f'{_(1)}]',
        f'{_(1)}UnknownInputType: te.TypeAlias = t.Union[UnknownType, t.Dict[str, t.Any]]',
        'else:',
        # the runtime annotation carries no member list: records are resolved through the registry,
        # so a package generated from custom lexicons is decoded here too
        f'{_(1)}UnknownType = te.Annotated[t.Any, unknown_union.UnknownRecordFallback]',
        f'{_(1)}UnknownInputType = UnknownType',
    ]
    if config.is_self_gen:
        unknown_type_lines.append(
            'UnknownRecordTypePydantic = UnknownType  #: Deprecated alias of :obj:`UnknownType`. Use it instead.'
        )

    write_code(config.models_output_dir.joinpath('type_conversion.py'), join_code(type_conversion_lines))
    write_code(config.models_output_dir.joinpath('unknown_type.py'), join_code(unknown_type_lines))


def _generate_empty_init_files(root_package_path: Path) -> None:
    for root, __, ___ in os.walk(root_package_path):
        root_path = Path(root)

        # the package __init__.py is generated by _generate_import_aliases
        if root_path == root_package_path or root_path.name == '__pycache__':
            continue

        write_code(root_path.joinpath('__init__.py'), DISCLAIMER)


def _generate_import_aliases() -> None:
    """Generate the models package __init__.py.

    The package defines ~1k pydantic models across hundreds of modules. Importing all of them
    eagerly used to make `import atproto` take several seconds. Instead, every model
    module is exposed lazily via a module-level __getattr__.
    """
    config = get_config()
    base = f'{config.base_package}.models'

    type_checking_imports = []
    aliases = []
    ids_db = ['class _Ids:']

    modules = {nsid: get_module_path_parts(nsid) for nsid in _nsid_with_imports}
    for nsid, (*packages, module_name) in sorted(
        modules.items(), key=lambda item: ('/'.join(item[1][:-1]), item[1][-1])
    ):
        alias_name = get_import_path(nsid)
        from_import = '.'.join([config.models_package, *packages])

        ids_db.append(f'{_(1)}{alias_name}: str = {str(nsid)!r}')
        type_checking_imports.append(f'{_(1)}from {from_import} import {module_name} as {alias_name}')
        aliases.append(alias_name)

    lazy_accessor_fallback = '' if config.is_self_gen else f", fallback='{base}'"

    # The TYPE_CHECKING import block (so type checkers/IDEs resolve every `models.Alias` symbol)
    # The _Ids registry (alias -> NSID, from which the runtime derives module paths)
    lines = [
        'import typing as t',
        f'from {base}.models_loader import make_lazy_accessors',
        # imported for its registration side effect; the redundant alias is what keeps F401 off it
        f'from {config.models_package} import type_conversion as type_conversion',
        'if t.TYPE_CHECKING:',
        *type_checking_imports,
        f'{_(1)}from {base}.utils import (',
        *[f'{_(2)}{name},' for name in sorted(_UTILS_EXPORTS)],
        f'{_(1)})',
        f'__getattr__, __dir__ = make_lazy_accessors(__name__{lazy_accessor_fallback})',
        '__all__ = [',
        *[f"{_(1)}'{name}'," for name in [*aliases, *sorted(_UTILS_EXPORTS), 'ids', 'type_conversion']],
        ']',
        *ids_db,
        'ids = _Ids()',
    ]

    write_code(config.models_output_dir.joinpath('__init__.py'), join_code(lines))


def _move_modules_shadowed_by_packages() -> None:
    """Move each module shadowed by a same-named package into that package's ``__init__.py``."""
    for nsid in _nsid_with_imports:
        module_path = _model_path(nsid)
        package_path = module_path.with_suffix('')
        if module_path.is_file() and package_path.is_dir():
            module_path.replace(package_path.joinpath('__init__.py'))


def _generate_package_init(config: CodegenConfig) -> None:
    """Make the generated package importable. The SDK's own root is hand-written, so it is skipped."""
    if config.is_self_gen:
        return

    init_path = config.output_dir.joinpath('__init__.py')
    if not init_path.exists():
        write_code(init_path, DISCLAIMER)


def _check_references(config: CodegenConfig) -> None:
    lexicons = builder.parse_lexicons(config)
    if config.skip_invalid:
        # such a run resolves every reference where it is used and weakens the ones it can not
        return

    unresolved = find_unresolved_refs(lexicons)
    if not config.is_self_gen:
        emitted = {lexicon.id for lexicon in lexicons}
        unresolved = {target: refs for target, refs in unresolved.items() if target.split('#')[0] in emitted}

    if unresolved:
        lines = [f"- '{target}' referenced by {', '.join(referrers)}" for target, referrers in unresolved.items()]
        raise UnresolvedReferenceError('\n'.join(['Lexicons reference missing definitions:', *lines]))


def generate_models(config: t.Optional[CodegenConfig] = None) -> None:
    with use_config(config or get_config()) as active:
        _check_references(active)
        _nsid_with_imports.clear()
        _inline_models.clear()
        _pending_inline_models.clear()

        _generate_params_models(builder.build_params_models(active))
        _generate_data_models(builder.build_data_models(active))
        _generate_response_models(builder.build_response_models(active))
        _generate_def_models(builder.build_def_models(active))

        _generate_record_models(builder.build_record_models(active))
        _generate_inline_models()
        _generate_record_type_database(builder.build_record_models(active))

        _generate_empty_init_files(active.models_output_dir)
        _generate_import_aliases()
        _generate_package_init(active)

        format_code(active.models_output_dir, root=active.output_dir)
        # after formatting: ruff keeps unused imports in __init__.py
        _move_modules_shadowed_by_packages()

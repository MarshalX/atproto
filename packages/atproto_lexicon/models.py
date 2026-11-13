import re
import typing as t

import typing_extensions as te
from atproto_core.exceptions import InvalidNsidError
from atproto_core.nsid import validate_nsid
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class LexDefinitionType:
    RECORD: te.Final = 'record'

    QUERY: te.Final = 'query'
    PROCEDURE: te.Final = 'procedure'
    SUBSCRIPTION: te.Final = 'subscription'

    PARAMS: te.Final = 'params'
    TOKEN: te.Final = 'token'  # noqa: S105
    OBJECT: te.Final = 'object'

    BLOB: te.Final = 'blob'
    ARRAY: te.Final = 'array'

    BOOLEAN: te.Final = 'boolean'
    INTEGER: te.Final = 'integer'
    STRING: te.Final = 'string'
    BYTES: te.Final = 'bytes'
    CID_LINK: te.Final = 'cid-link'

    PERMISSION: te.Final = 'permission'
    PERMISSION_SET: te.Final = 'permission-set'


class LexPrimitiveType:
    BOOLEAN: te.Final = 'boolean'
    INTEGER: te.Final = 'integer'
    STRING: te.Final = 'string'
    REF: te.Final = 'ref'
    UNION: te.Final = 'union'
    UNKNOWN: te.Final = 'unknown'
    CID_LINK: te.Final = 'cid-link'
    BYTES: te.Final = 'bytes'


_RECORD_KEY_TYPES = frozenset({'any', 'nsid', 'tid'})
_RECORD_KEY_LITERAL_PREFIX = 'literal:'
_RECORD_KEY_REGEX = re.compile(r'^[a-zA-Z0-9._:~-]{1,512}$')
_RECORD_KEY_FORBIDDEN = frozenset({'.', '..'})

_DEF_NAME_FORBIDDEN_CHARS = ('#', '.')
_ENCODING_FORBIDDEN_CHARS = (',', ';', ' ')
_MAIN_DEF_NAME = 'main'


def _check_listed_properties(listed: t.Optional[t.List[str]], properties: t.Dict[str, t.Any], field: str) -> None:
    for name in listed or []:
        if name not in properties:
            raise ValueError(f"'{field}' lists '{name}', which is not defined in 'properties'")


class LexBase(BaseModel):
    """Base class for all lexicon models.

    Unknown fields are ignored, as in the reference implementations.
    """

    model_config = ConfigDict(extra='ignore', populate_by_name=True, strict=True)


class LexDefinitionBase(LexBase):  # original name LexUserType
    """Base class for all lexicon definitions."""

    description: t.Optional[str] = None


class LexPrimitiveBase(LexBase):
    """Base class for all lexicon primitives."""

    description: t.Optional[str] = None


class LexXrpcError(LexBase):
    name: str = Field(min_length=1)
    description: t.Optional[str] = None


class LexUnknown(LexPrimitiveBase):
    type: te.Literal['unknown'] = Field(default=LexPrimitiveType.UNKNOWN, frozen=True)


class LexCidLink(LexPrimitiveBase):
    type: te.Literal['cid-link'] = Field(default=LexPrimitiveType.CID_LINK, frozen=True)


class LexBytes(LexPrimitiveBase):
    type: te.Literal['bytes'] = Field(default=LexPrimitiveType.BYTES, frozen=True)

    max_length: t.Optional[int] = Field(default=None, alias='maxLength')
    min_length: t.Optional[int] = Field(default=None, alias='minLength')


class LexBoolean(LexPrimitiveBase):
    type: te.Literal['boolean'] = Field(default=LexPrimitiveType.BOOLEAN, frozen=True)

    default: t.Optional[bool] = None
    const: t.Optional[bool] = None


class LexInteger(LexPrimitiveBase):
    type: te.Literal['integer'] = Field(default=LexPrimitiveType.INTEGER, frozen=True)

    default: t.Optional[int] = None
    minimum: t.Optional[int] = None
    maximum: t.Optional[int] = None
    enum: t.Optional[t.List[int]] = None
    const: t.Optional[int] = None


class LexString(LexPrimitiveBase):
    type: te.Literal['string'] = Field(default=LexPrimitiveType.STRING, frozen=True)

    format: t.Optional[str] = None
    default: t.Optional[str] = None
    min_length: t.Optional[int] = Field(default=None, alias='minLength')
    max_length: t.Optional[int] = Field(default=None, alias='maxLength')
    min_graphemes: t.Optional[int] = Field(default=None, alias='minGraphemes')
    max_graphemes: t.Optional[int] = Field(default=None, alias='maxGraphemes')
    enum: t.Optional[t.List[str]] = None
    const: t.Optional[str] = None
    known_values: t.Optional[t.List[str]] = Field(default=None, alias='knownValues')


class LexRef(LexPrimitiveBase):
    type: te.Literal['ref'] = Field(default=LexPrimitiveType.REF, frozen=True)

    ref: str


class LexRefUnion(LexPrimitiveBase):
    type: te.Literal['union'] = Field(default=LexPrimitiveType.UNION, frozen=True)

    refs: t.List[str]
    closed: t.Optional[bool] = False


LexRefVariant = te.Annotated[t.Union[LexRef, LexRefUnion], Field(discriminator='type')]
LexPrimitive = te.Annotated[
    t.Union[
        LexUnknown,
        LexCidLink,
        LexBytes,
        LexBoolean,
        LexInteger,
        LexString,
        LexRef,
        LexRefVariant,
    ],
    Field(discriminator='type'),
]

_PARAMETER_PRIMITIVE_TYPES = frozenset({LexPrimitiveType.BOOLEAN, LexPrimitiveType.INTEGER, LexPrimitiveType.STRING})


class LexBlob(LexDefinitionBase):
    type: te.Literal['blob'] = Field(default=LexDefinitionType.BLOB, frozen=True)

    accept: t.Optional[t.List[str]] = None
    max_size: t.Optional[int] = Field(default=None, alias='maxSize')


class LexArray(LexDefinitionBase):
    type: te.Literal['array'] = Field(default=LexDefinitionType.ARRAY, frozen=True)

    items: t.Union[
        LexRefVariant, te.Annotated[t.Union[LexPrimitive, LexBlob, 'LexObject'], Field(discriminator='type')]
    ]
    min_length: t.Optional[int] = Field(default=None, alias='minLength')
    max_length: t.Optional[int] = Field(default=None, alias='maxLength')


class LexToken(LexDefinitionBase):
    type: te.Literal['token'] = Field(default=LexDefinitionType.TOKEN, frozen=True)


class LexObject(LexDefinitionBase):
    type: te.Literal['object'] = Field(default=LexDefinitionType.OBJECT, frozen=True)

    required: t.Optional[t.List[str]] = None
    nullable: t.Optional[t.List[str]] = None
    properties: t.Dict[
        str, te.Annotated[t.Union[LexPrimitive, LexArray, LexBlob, 'LexObject'], Field(discriminator='type')]
    ] = Field(default_factory=dict)

    @model_validator(mode='after')
    def _check_listed_properties(self) -> te.Self:
        _check_listed_properties(self.required, self.properties, 'required')
        _check_listed_properties(self.nullable, self.properties, 'nullable')
        return self


class LexRecord(LexDefinitionBase):
    type: te.Literal['record'] = Field(default=LexDefinitionType.RECORD, frozen=True)

    key: str
    record: LexObject

    @field_validator('key')
    @classmethod
    def _check_key(cls, key: str) -> str:
        if key in _RECORD_KEY_TYPES:
            return key

        literal = key[len(_RECORD_KEY_LITERAL_PREFIX) :]
        is_literal = key.startswith(_RECORD_KEY_LITERAL_PREFIX)
        if not is_literal or not _RECORD_KEY_REGEX.match(literal) or literal in _RECORD_KEY_FORBIDDEN:
            raise ValueError("Record key must be 'any', 'nsid', 'tid' or 'literal:<record key>'")

        return key


class LexXrpcParameters(LexDefinitionBase):
    type: te.Literal['params'] = Field(default=LexDefinitionType.PARAMS, frozen=True)

    required: t.Optional[t.List[str]] = None
    properties: t.Dict[
        str, te.Annotated[t.Union[LexBoolean, LexInteger, LexString, LexArray], Field(discriminator='type')]
    ]

    @model_validator(mode='after')
    def _check_properties(self) -> te.Self:
        _check_listed_properties(self.required, self.properties, 'required')
        arrays = {name: prop.items for name, prop in self.properties.items() if isinstance(prop, LexArray)}
        invalid = sorted(name for name, items in arrays.items() if items.type not in _PARAMETER_PRIMITIVE_TYPES)
        if invalid:
            raise ValueError(f'Items of array parameters must be boolean, integer or string: {", ".join(invalid)}')
        return self


class LexXrpcSubscriptionMessage(LexBase):
    description: t.Optional[str] = None
    schema_: LexRefUnion = Field(alias='schema')


class LexXrpcBody(LexBase):
    description: t.Optional[str] = None
    encoding: str
    schema_: t.Optional[te.Annotated[t.Union[LexObject, LexRefVariant], Field(discriminator='type')]] = Field(
        default=None, alias='schema'
    )

    @field_validator('encoding')
    @classmethod
    def _check_encoding(cls, encoding: str) -> str:
        if any(char in encoding for char in _ENCODING_FORBIDDEN_CHARS):
            raise ValueError('Encoding must be a single MIME type without parameters')
        return encoding


class LexSubscription(LexDefinitionBase):
    type: te.Literal['subscription'] = Field(default=LexDefinitionType.SUBSCRIPTION, frozen=True)

    parameters: t.Optional[LexXrpcParameters] = None
    message: LexXrpcSubscriptionMessage
    infos: t.Optional[t.List[LexXrpcError]] = None
    errors: t.Optional[t.List[LexXrpcError]] = None
    subprotocol: t.Optional[str] = None


class LexXrpcQuery(LexDefinitionBase):
    type: te.Literal['query'] = Field(default=LexDefinitionType.QUERY, frozen=True)

    parameters: t.Optional[LexXrpcParameters] = None
    output: t.Optional[LexXrpcBody] = None
    errors: t.Optional[t.List[LexXrpcError]] = None


class LexXrpcProcedure(LexDefinitionBase):
    type: te.Literal['procedure'] = Field(default=LexDefinitionType.PROCEDURE, frozen=True)

    parameters: t.Optional[LexXrpcParameters] = None
    input: t.Optional[LexXrpcBody] = None
    output: t.Optional[LexXrpcBody] = None
    errors: t.Optional[t.List[LexXrpcError]] = None


class LexPermission(LexDefinitionBase):
    model_config = ConfigDict(extra='allow', populate_by_name=True, strict=True)

    type: te.Literal['permission'] = Field(default=LexDefinitionType.PERMISSION, frozen=True)
    resource: str = Field(min_length=1)


LexLang = te.Dict[str, te.Optional[str]]


class LexPermissionSet(LexDefinitionBase):
    type: te.Literal['permission-set'] = Field(default=LexDefinitionType.PERMISSION_SET, frozen=True)
    description: te.Optional[str] = None
    title: te.Optional[str] = None
    title_lang: te.Optional[LexLang] = Field(default=None, alias='title:lang')
    detail: te.Optional[str] = None
    detail_lang: te.Optional[LexLang] = Field(default=None, alias='detail:lang')
    permissions: te.List[LexPermission]


LexMainDefinition = (LexRecord, LexSubscription, LexXrpcQuery, LexXrpcProcedure, LexPermissionSet)
"""Definitions allowed only under the name ``main``."""

LexDefinition = te.Annotated[
    t.Union[
        LexBlob,
        LexArray,
        LexToken,
        LexObject,
        LexRecord,
        LexSubscription,
        LexXrpcQuery,
        LexXrpcProcedure,
        LexPermissionSet,
        LexBoolean,
        LexInteger,
        LexString,
        LexBytes,
        LexCidLink,
    ],
    Field(discriminator='type'),
]


class LexiconDoc(LexBase):
    """Lexicon document model."""

    lexicon: te.Literal[1]
    id: str  # NSID
    defs: t.Dict[str, LexDefinition]
    description: t.Optional[str] = None
    revision: t.Optional[int] = None

    @field_validator('id')
    @classmethod
    def _check_id(cls, nsid: str) -> str:
        try:
            validate_nsid(nsid)
        except InvalidNsidError as e:
            raise ValueError(f'Lexicon ID must be a valid NSID: {e}') from e
        return nsid

    @model_validator(mode='after')
    def _check_defs(self) -> te.Self:
        for name, definition in self.defs.items():
            if not name or any(char in name for char in _DEF_NAME_FORBIDDEN_CHARS):
                raise ValueError(f"Invalid definition name '{name}'")
            if name != _MAIN_DEF_NAME and isinstance(definition, LexMainDefinition):
                raise ValueError(f"Definition '{name}' of type '{definition.type}' is allowed only as 'main'")
        return self

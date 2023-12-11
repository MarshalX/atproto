import typing as t
from dataclasses import dataclass
from enum import Enum

Number = t.Union[int, float, complex]


class LexDefinitionType(Enum):
    RECORD = 'record'

    QUERY = 'query'
    PROCEDURE = 'procedure'
    SUBSCRIPTION = 'subscription'

    PARAMS = 'params'
    TOKEN = 'token'  # noqa: S105
    OBJECT = 'object'

    BLOB = 'blob'
    ARRAY = 'array'

    STRING = 'string'  # TODO(MarshalX): definitions could be primitives?


class LexPrimitiveType(Enum):
    BOOLEAN = 'boolean'
    NUMBER = 'number'
    INTEGER = 'integer'
    STRING = 'string'
    REF = 'ref'
    UNION = 'union'
    UNKNOWN = 'unknown'
    CID_LINK = 'cid-link'
    BYTES = 'bytes'


@dataclass
class LexDefinition:  # original name LexUserType
    type: LexDefinitionType
    description: t.Optional[str]


@dataclass
class LexPrimitive:
    type: LexPrimitiveType
    description: t.Optional[str]


@dataclass
class LexUnknown(LexPrimitive):
    type = LexPrimitiveType.UNKNOWN


@dataclass
class LexCidLink(LexPrimitive):
    type = LexPrimitiveType.CID_LINK


@dataclass
class LexBytes(LexPrimitive):
    type = LexPrimitiveType.BYTES
    maxLength: t.Optional[Number]
    minLength: t.Optional[Number]


@dataclass
class LexBoolean(LexPrimitive):
    type = LexPrimitiveType.BOOLEAN
    default: t.Optional[bool]
    const: t.Optional[bool]


@dataclass
class LexNumber(LexPrimitive):
    type = LexPrimitiveType.NUMBER
    default: t.Optional[Number]
    minimum: t.Optional[Number]
    maximum: t.Optional[Number]
    enum: t.Optional[t.List[Number]]
    const: t.Optional[Number]


@dataclass
class LexInteger(LexPrimitive):
    type = LexPrimitiveType.INTEGER
    default: t.Optional[int]
    minimum: t.Optional[int]
    maximum: t.Optional[int]
    enum: t.Optional[t.List[int]]
    const: t.Optional[int]


@dataclass
class LexString(LexPrimitive):
    type = LexPrimitiveType.STRING
    format: t.Optional[str]
    default: t.Optional[str]
    minLength: t.Optional[int]
    maxLength: t.Optional[int]
    minGraphemes: t.Optional[int]
    maxGraphemes: t.Optional[int]
    enum: t.Optional[t.List[str]]
    const: t.Optional[str]
    knownValues: t.Optional[t.List[str]]


@dataclass
class LexBlob(LexDefinition):
    type = LexDefinitionType.BLOB
    accept: t.Optional[t.List[str]]
    maxSize: t.Optional[Number]


@dataclass
class LexRef(LexPrimitive):
    type = LexPrimitiveType.REF
    ref: str


@dataclass
class LexRefUnion(LexPrimitive):
    type = LexPrimitiveType.UNION
    refs: t.List[str]
    closed: t.Optional[bool]


LexRefVariant = t.Union[LexRef, LexRefUnion]


@dataclass
class LexArray(LexDefinition):
    type = LexDefinitionType.ARRAY
    description: t.Optional[str]
    items: t.Union[LexPrimitive, LexBlob, LexRefVariant]
    minLength: t.Optional[int]
    maxLength: t.Optional[int]


@dataclass
class LexiconDoc:
    lexicon: int
    id: str  # an NSID
    revision: t.Optional[int]
    description: t.Optional[str]
    defs: t.Dict[str, LexDefinition]


@dataclass
class LexToken(LexDefinition):
    type = LexDefinitionType.TOKEN


@dataclass
class LexObject(LexDefinition):
    type = LexDefinitionType.OBJECT
    required: t.Optional[t.List[str]]
    nullable: t.Optional[t.List[str]]
    properties: t.Dict[str, t.Union[LexRefVariant, LexArray, LexPrimitive, LexBlob]]


@dataclass
class LexRecord(LexDefinition):
    type = LexDefinitionType.RECORD
    key: t.Optional[str]
    record: LexObject


@dataclass
class LexXrpcParameters(LexDefinition):
    type = LexDefinitionType.PARAMS
    description: t.Optional[str]
    required: t.Optional[t.List[str]]
    properties: t.Dict[str, t.Union[LexArray, LexPrimitive]]


@dataclass
class LexXrpcSubscriptionMessage:
    description: t.Optional[str]
    schema: t.Optional[t.Union[LexObject, LexRefVariant]]


@dataclass
class LexXrpcBody:
    description: t.Optional[str]
    encoding: t.Union[str, t.List[str]]
    schema: t.Optional[t.Union[LexObject, LexRefVariant]]


@dataclass
class LexXrpcError:
    name: str
    description: t.Optional[str]


@dataclass
class LexSubscription(LexDefinition):
    type = LexDefinitionType.SUBSCRIPTION
    parameters: t.Optional[LexXrpcParameters]
    message: t.Optional[LexXrpcSubscriptionMessage]
    infos: t.Optional[t.List[LexXrpcError]]
    errors: t.Optional[t.List[LexXrpcError]]


@dataclass
class LexXrpcQuery(LexDefinition):
    type = LexDefinitionType.QUERY
    parameters: t.Optional[LexXrpcParameters]
    output: t.Optional[LexXrpcBody]
    errors: t.Optional[t.List[LexXrpcError]]


@dataclass
class LexXrpcProcedure(LexDefinition):
    type = LexDefinitionType.PROCEDURE
    parameters: t.Optional[LexXrpcParameters]
    input: t.Optional[LexXrpcBody]
    output: t.Optional[LexXrpcBody]
    errors: t.Optional[t.List[LexXrpcError]]

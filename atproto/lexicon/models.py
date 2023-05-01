from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

LexRef = str
Number = Union[int, float, complex]


class LexDefinitionType(Enum):
    RECORD = 'record'

    QUERY = 'query'
    PROCEDURE = 'procedure'
    SUBSCRIPTION = 'subscription'

    PARAMS = 'params'
    TOKEN = 'token'
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
    description: Optional[str]


@dataclass
class LexPrimitive:
    type: LexPrimitiveType
    description: Optional[str]


@dataclass
class LexUnknown(LexPrimitive):
    type = LexPrimitiveType.UNKNOWN


@dataclass
class LexCidLink(LexPrimitive):
    type = LexPrimitiveType.CID_LINK


@dataclass
class LexBytes(LexPrimitive):
    type = LexPrimitiveType.BYTES
    maxLength: Optional[Number]
    minLength: Optional[Number]


@dataclass
class LexBoolean(LexPrimitive):
    type = LexPrimitiveType.BOOLEAN
    default: Optional[bool]
    const: Optional[bool]


@dataclass
class LexNumber(LexPrimitive):
    type = LexPrimitiveType.NUMBER
    default: Optional[Number]
    minimum: Optional[Number]
    maximum: Optional[Number]
    enum: Optional[List[Number]]
    const: Optional[Number]


@dataclass
class LexInteger(LexPrimitive):
    type = LexPrimitiveType.INTEGER
    default: Optional[int]
    minimum: Optional[int]
    maximum: Optional[int]
    enum: Optional[List[int]]
    const: Optional[int]


@dataclass
class LexString(LexPrimitive):
    type = LexPrimitiveType.STRING
    format: Optional[str]
    default: Optional[str]
    minLength: Optional[int]
    maxLength: Optional[int]
    minGraphemes: Optional[int]
    maxGraphemes: Optional[int]
    enum: Optional[List[str]]
    const: Optional[str]
    knownValues: Optional[List[str]]


@dataclass
class LexBlob(LexDefinition):
    type = LexDefinitionType.BLOB
    accept: Optional[List[str]]
    maxSize: Optional[Number]


@dataclass
class LexRef(LexPrimitive):
    type = LexPrimitiveType.REF
    ref: str


@dataclass
class LexRefUnion(LexPrimitive):
    type = LexPrimitiveType.UNION
    refs: List[str]
    closed: Optional[bool]


LexRefVariant = Union[LexRef, LexRefUnion]


@dataclass
class LexArray(LexDefinition):
    type = LexDefinitionType.ARRAY
    description: Optional[str]
    items: Union[LexPrimitive, LexBlob, LexRefVariant]
    minLength: Optional[int]
    maxLength: Optional[int]


@dataclass
class LexiconDoc:
    lexicon: int
    id: str  # an NSID
    revision: Optional[int]
    description: Optional[str]
    defs: Dict[str, LexDefinition]


@dataclass
class LexToken(LexDefinition):
    type = LexDefinitionType.TOKEN


@dataclass
class LexObject(LexDefinition):
    type = LexDefinitionType.OBJECT
    required: Optional[List[str]]
    nullable: Optional[List[str]]
    properties: Dict[str, Union[LexRefVariant, LexArray, LexPrimitive, LexBlob]]


@dataclass
class LexRecord(LexDefinition):
    type = LexDefinitionType.RECORD
    key: Optional[str]
    record: LexObject


@dataclass
class LexXrpcParameters(LexDefinition):
    type = LexDefinitionType.PARAMS
    description: Optional[str]
    required: Optional[List[str]]
    properties: Dict[str, Union[LexArray, LexPrimitive]]


@dataclass
class LexXrpcSubscriptionMessage:
    description: Optional[str]
    schema: Optional[Union[LexObject, LexRefVariant]]


@dataclass
class LexXrpcBody:
    description: Optional[str]
    encoding: Union[str, List[str]]
    schema: Optional[Union[LexObject, LexRefVariant]]


@dataclass
class LexXrpcError:
    name: str
    description: Optional[str]


@dataclass
class LexSubscription(LexDefinition):
    type = LexDefinitionType.SUBSCRIPTION
    parameters: Optional[LexXrpcParameters]
    message: Optional[LexXrpcSubscriptionMessage]
    infos: Optional[List[LexXrpcError]]
    errors: Optional[List[LexXrpcError]]


@dataclass
class LexXrpcQuery(LexDefinition):
    type = LexDefinitionType.QUERY
    parameters: Optional[LexXrpcParameters]
    output: Optional[LexXrpcBody]
    errors: Optional[List[LexXrpcError]]


@dataclass
class LexXrpcProcedure(LexDefinition):
    type = LexDefinitionType.PROCEDURE
    parameters: Optional[Dict[str, LexPrimitive]]
    input: Optional[LexXrpcBody]
    output: Optional[LexXrpcBody]
    errors: Optional[List[LexXrpcError]]

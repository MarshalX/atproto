from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Union

LexRef = str
Number = Union[int, float, complex]


class LexDefinitionType(Enum):
    QUERY = 'query'
    PROCEDURE = 'procedure'
    RECORD = 'record'
    TOKEN = 'token'
    OBJECT = 'object'
    BLOB = 'blob'
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'


class LexPrimitiveType(Enum):
    BOOLEAN = 'boolean'
    NUMBER = 'number'
    INTEGER = 'integer'
    STRING = 'string'
    # FIXME(MarshalX): more undocumented types?
    REF = 'ref'


@dataclass
class LexDefinition:  # original name LexUserType
    type: LexDefinitionType
    description: Optional[str]


@dataclass
class LexPrimitive:
    type: LexPrimitiveType
    description: Optional[str]


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
    # TODO(MarshalX): "format" is missing in docs? could be "handle", "did", etc
    format: Optional[str]
    type = LexPrimitiveType.STRING
    default: Optional[str]
    minLength: Optional[int]
    maxLength: Optional[int]
    enum: Optional[List[str]]
    const: Optional[str]
    knownValues: Optional[List[str]]


@dataclass
class LexRef(LexPrimitive):
    # TODO(MarshalX): not documented. mb not full model
    type = LexPrimitiveType.REF
    ref: str


@dataclass
class LexArray:
    type = 'array'
    description: Optional[str]
    items: Union[LexRef, LexPrimitive, List[LexRef]]
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
    properties: Dict[str, Union[LexRef, LexArray, LexPrimitive, List[LexRef]]]


@dataclass
class LexXrpcBody:
    description: Optional[str]
    encoding: Union[str, List[str]]
    schema: LexObject


@dataclass
class LexXrpcError:
    name: str
    description: Optional[str]


@dataclass
class LexXrpcQuery(LexDefinition):
    type = LexDefinitionType.QUERY
    parameters: Optional[Dict[str, LexPrimitive]]
    output: Optional[LexXrpcBody]
    errors: Optional[List[LexXrpcError]]


@dataclass
class LexXrpcProcedure(LexDefinition):
    type = LexDefinitionType.PROCEDURE
    parameters: Optional[Dict[str, LexPrimitive]]
    input: Optional[LexXrpcBody]
    output: Optional[LexXrpcBody]
    errors: Optional[List[LexXrpcError]]

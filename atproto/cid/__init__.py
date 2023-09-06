import typing as t
from dataclasses import dataclass

import libipld
import typing_extensions as te
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema


@dataclass
class Multihash:
    code: int
    size: int
    digest: bytes


@dataclass
class CID:
    _cid: str
    version: int
    codec: int
    hash: Multihash

    @classmethod
    def decode(cls, value: str) -> 'CID':
        cid = libipld.decode_cid(value)

        multihash = Multihash(
            code=cid['hash']['code'],
            size=cid['hash']['size'],
            digest=cid['hash']['digest'],
        )

        return cls(
            _cid=value,
            version=cid['version'],
            codec=cid['codec'],
            hash=multihash,
        )

    def encode(self) -> str:
        return self._cid

    def __str__(self) -> str:
        return self.encode()

    def __hash__(self):
        return hash(self.encode())


class _CIDPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: t.Any,
        _handler: t.Callable[[t.Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """
        We return a pydantic_core.CoreSchema that behaves in the following ways:

        * Strings will be parsed as `CID` instances
        * `CID` instances will be parsed as `CID` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a str
        """

        def validate_from_str(value: str) -> CID:
            return CID.decode(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_str),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(CID),
                    from_str_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(lambda instance: instance.encode()),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        # Use the same schema that would be used for `str`
        return handler(core_schema.str_schema())


CIDType = te.Annotated[CID, _CIDPydanticAnnotation]

import typing as t

import libipld
import typing_extensions as te
from pydantic import GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema

CID = libipld.CID
Multihash = libipld.Multihash


class _CIDPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: t.Any,
        _handler: t.Callable[[t.Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """Accept a `CID`, or its string or binary form; serialize to the string form."""
        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(CID),
            ]
        )

        from_bytes_schema = core_schema.chain_schema(
            [
                core_schema.bytes_schema(),
                core_schema.no_info_plain_validator_function(CID),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(CID),
                    from_str_schema,
                    from_bytes_schema,
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: core_schema.CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(core_schema.str_schema())


CIDType = te.Annotated[CID, _CIDPydanticAnnotation]

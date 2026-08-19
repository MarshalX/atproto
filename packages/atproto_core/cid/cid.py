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


class CID:
    """Content Identifier.

    Note:
        `version`, `codec`, and `hash` are decoded lazily on first access. Consumers that only
        compare or stringify CIDs (the CAR decoding path, for one) never pay for the multihash.
    """

    __slots__ = ('_codec', '_hash', '_raw_byte_form', '_stringified_form', '_version')

    def __init__(
        self,
        version: t.Optional[int] = None,
        codec: t.Optional[int] = None,
        hash: t.Optional[Multihash] = None,
        _stringified_form: t.Optional[str] = None,
        _raw_byte_form: t.Optional[bytes] = None,
    ) -> None:
        self._version = version
        self._codec = codec
        self._hash = hash
        self._stringified_form = _stringified_form
        self._raw_byte_form = _raw_byte_form

    @classmethod
    def decode(cls, value: t.Union[str, bytes]) -> 'CID':
        cid = libipld.decode_cid(value)

        multihash = Multihash(
            code=cid['hash']['code'],
            size=cid['hash']['size'],
            digest=cid['hash']['digest'],
        )

        instance = cls(
            version=cid['version'],
            codec=cid['codec'],
            hash=multihash,
        )

        if isinstance(value, str):
            instance._stringified_form = value
        else:
            instance._raw_byte_form = value

        return instance

    @classmethod
    def from_decoded_bytes(cls, value: bytes) -> 'CID':
        """Wrap the binary form of a CID that the decoder it came from has already validated.

        Skips the redundant :obj:`libipld.decode_cid` call that :obj:`CID.decode` performs.
        """
        return cls(_raw_byte_form=value)

    def _encoded_form(self) -> t.Union[str, bytes]:
        encoded = self._raw_byte_form if self._raw_byte_form is not None else self._stringified_form
        if encoded is None:
            raise ValueError('CID was built without an encoded form')

        return encoded

    def _decode_lazy_fields(self) -> None:
        cid = libipld.decode_cid(self._encoded_form())

        self._version = cid['version']
        self._codec = cid['codec']
        self._hash = Multihash(
            code=cid['hash']['code'],
            size=cid['hash']['size'],
            digest=cid['hash']['digest'],
        )

    @property
    def version(self) -> int:
        """Get CID version."""
        if self._version is None:
            self._decode_lazy_fields()

        return t.cast('int', self._version)

    @property
    def codec(self) -> int:
        """Get CID codec."""
        if self._codec is None:
            self._decode_lazy_fields()

        return t.cast('int', self._codec)

    @property
    def hash(self) -> Multihash:
        """Get CID multihash."""
        if self._hash is None:
            self._decode_lazy_fields()

        return t.cast('Multihash', self._hash)

    def encode(self) -> str:
        if self._stringified_form is not None:
            return self._stringified_form

        if self._raw_byte_form is None:
            raise ValueError('CID was built without an encoded form')

        self._stringified_form = libipld.encode_cid(self._raw_byte_form)
        return self._stringified_form

    def __repr__(self) -> str:
        return (
            f'CID(version={self.version}, codec={self.codec}, hash={self.hash!r}, '
            f'_stringified_form={self._stringified_form!r}, _raw_byte_form={self._raw_byte_form!r})'
        )

    def __str__(self) -> str:
        return self.encode()

    def __hash__(self) -> int:
        return hash(self.encode())

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self.encode() == other

        if isinstance(other, CID):
            return self.encode() == other.encode()

        return False


class _CIDPydanticAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: t.Any,
        _handler: t.Callable[[t.Any], core_schema.CoreSchema],
    ) -> core_schema.CoreSchema:
        """We return a pydantic_core.CoreSchema that behaves in the following ways below.

        * Strings and bytes will be parsed as `CID` instances
        * `CID` instances will be parsed as `CID` instances without any changes
        * Nothing else will pass validation
        * Serialization will always return just a str
        """

        def validate_from_value(value: t.Union[str, bytes]) -> CID:
            return CID.decode(value)

        from_str_schema = core_schema.chain_schema(
            [
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(validate_from_value),
            ]
        )

        from_bytes_schema = core_schema.chain_schema(
            [
                core_schema.bytes_schema(),
                core_schema.no_info_plain_validator_function(validate_from_value),
            ]
        )

        return core_schema.json_or_python_schema(
            json_schema=from_str_schema,
            python_schema=core_schema.union_schema(
                [
                    # check if it's an instance first before doing any further work
                    core_schema.is_instance_schema(CID),
                    from_str_schema,
                    from_bytes_schema,
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

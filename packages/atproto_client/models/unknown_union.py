import typing as t

import typing_extensions as te
from pydantic import BaseModel, Field, GetCoreSchemaHandler, ValidationError
from pydantic_core import core_schema

from atproto_client.models.dot_dict import DotDict, DotDictType

_TAG_ERROR_TYPES = frozenset({'union_tag_invalid', 'union_tag_not_found'})


def _is_unknown_tag_error(exc: ValidationError) -> bool:
    errors = exc.errors()
    return bool(errors) and all(e['type'] in _TAG_ERROR_TYPES and not e['loc'] for e in errors)


class UnknownUnionFallback:
    """Annotation for open ref unions: an unrecognized ``$type`` falls back to :obj:`DotDict`.

    Applied to ``t.Union[<known members>, 'dot_dict.DotDictType']``. Members are discriminated by
    ``py_type`` as usual, so a known type that fails validation still raises. Only a ``$type`` that
    matches no member, or a missing one, degrades to a :obj:`DotDict`.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: t.Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        members = tuple(arg for arg in t.get_args(source_type) if arg is not DotDictType)
        discriminated = te.Annotated[t.Union[members], Field(discriminator='py_type')]  # type: ignore[valid-type]

        def validate(value: t.Any, validator: core_schema.ValidatorFunctionWrapHandler) -> t.Any:
            try:
                return validator(value)
            except ValidationError as e:
                if isinstance(value, (dict, DotDict)) and _is_unknown_tag_error(e):
                    return DotDict(dict(value))

                raise

        def serialize(value: t.Any, serializer: core_schema.SerializerFunctionWrapHandler) -> t.Any:
            if isinstance(value, DotDict):
                return value.to_dict()

            return serializer(value)

        return core_schema.no_info_wrap_validator_function(
            validate,
            handler.generate_schema(discriminated),
            serialization=core_schema.wrap_serializer_function_ser_schema(serialize),
        )


_T = t.TypeVar('_T')

#: An open ref union: the described types, plus a :obj:`DotDict` for a ``$type`` released after this SDK.
OpenUnion: te.TypeAlias = te.Annotated[t.Union[_T, DotDictType], UnknownUnionFallback]


def _serialize_unknown(value: t.Any, serializer: t.Any, info: t.Any) -> t.Any:
    if isinstance(value, DotDict):
        return value.to_dict()

    if isinstance(value, BaseModel):
        return value.model_dump(
            mode=info.mode,
            by_alias=bool(info.by_alias),
            exclude_none=bool(info.exclude_none),
        )

    return serializer(value)


class UnknownRecordFallback:
    """Annotation for lexicon ``unknown`` fields: any registered record type, else :obj:`DotDict`.

    Record types are looked up in the runtime registry rather than in a union fixed at import time,
    so a record defined by a package generated from custom lexicons is decoded to its own model.
    """

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: t.Any, handler: GetCoreSchemaHandler) -> core_schema.CoreSchema:
        from atproto_client.models.record_registry import resolve_record_type

        def validate(
            value: t.Any, validator: core_schema.ValidatorFunctionWrapHandler, info: core_schema.ValidationInfo
        ) -> t.Any:
            if isinstance(value, BaseModel):
                return value

            data = value.to_dict() if isinstance(value, DotDict) else value
            if isinstance(data, dict):
                record_type = data.get('$type')
                model = resolve_record_type(record_type) if isinstance(record_type, str) else None
                if model is not None:
                    try:
                        return model.model_validate(data, context=info.context)
                    except ValidationError:
                        # a record the models know of but cannot describe still degrades to DotDict
                        pass

            return validator(value)

        return core_schema.with_info_wrap_validator_function(
            validate,
            handler.generate_schema(DotDictType),
            serialization=core_schema.wrap_serializer_function_ser_schema(_serialize_unknown, info_arg=True),
        )

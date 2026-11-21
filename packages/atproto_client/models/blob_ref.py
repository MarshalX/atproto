import typing as t

import typing_extensions as te
from atproto_core.cid import CID
from pydantic import BaseModel, ConfigDict, Field, InstanceOf, field_serializer


class IpldLink(BaseModel):
    """CID representation in JSON."""

    model_config = ConfigDict(extra='allow', populate_by_name=True, strict=True)

    link: str = Field(validation_alias='$link', serialization_alias='$link')  #: CID.


class BlobRef(BaseModel):
    """Blob reference."""

    model_config = ConfigDict(extra='allow', populate_by_name=True, strict=True)

    mime_type: str = Field(validation_alias='mimeType', serialization_alias='mimeType')  #: Mime type.
    size: int  #: Size in bytes.
    ref: t.Union[InstanceOf[CID], IpldLink, str, bytes]  #: CID.

    py_type: te.Literal['blob'] = Field(default='blob', validation_alias='$type', serialization_alias='$type')

    @field_serializer('ref', when_used='json')
    def _serialize_ref(self, ref: t.Union[CID, IpldLink, str, bytes]) -> t.Union[str, t.Dict[str, str]]:
        """Render a binary CID as the atproto JSON link. `model_dump` keeps it as it is."""
        if isinstance(ref, (CID, bytes)):
            return {'$link': str(CID(ref))}

        if isinstance(ref, IpldLink):
            return {'$link': ref.link}

        return ref

    @property
    def cid(self) -> 'CID':
        """Get CID."""
        if isinstance(self.ref, IpldLink):
            return CID(self.ref.link)

        return CID(self.ref)

    @property
    def is_json_representation(self) -> bool:
        """Check if it is JSON representation.

        Returns:
            True if it is JSON representation.
        """
        return isinstance(self.ref, IpldLink)

    @property
    def is_bytes_representation(self) -> bool:
        """Check if it is bytes representation.

        Returns:
            True if it is bytes representation.
        """
        return not isinstance(self.ref, IpldLink)

    def to_json_representation(self) -> 'BlobRef':
        """Get JSON representation.

        Note:
            Used in XRPC, etc. where JSON is used.

        Warning:
            It returns new instance.

        Returns:
            BlobRef in JSON representation.
        """
        if isinstance(self.ref, IpldLink):
            return BlobRef(mime_type=self.mime_type, size=self.size, ref=IpldLink(link=self.ref.link))

        return BlobRef(mime_type=self.mime_type, size=self.size, ref=IpldLink(link=str(self.cid)))

    def to_bytes_representation(self) -> 'BlobRef':
        """Get bytes representation.

        Note:
            Used in Firehose, CAR, etc. where bytes are possible.

        Warning:
            It returns new instance.

        Returns:
            BlobRef in bytes representation.
        """
        if isinstance(self.ref, IpldLink):
            return BlobRef(mime_type=self.mime_type, size=self.size, ref=CID(self.ref.link))

        return BlobRef(mime_type=self.mime_type, size=self.size, ref=self.ref)

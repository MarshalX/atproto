import typing as t

import typing_extensions as te
from pydantic import BaseModel, ConfigDict, Field

if t.TYPE_CHECKING:
    from atproto.cid import CID


class BlobRefLink(BaseModel):
    """Blob reference link."""

    link: str = Field(alias='$link')


class BlobRef(BaseModel):
    """Blob reference."""

    model_config = ConfigDict(extra='forbid', populate_by_name=True, strict=True)

    mime_type: str = Field(alias='mimeType')  #: Mime type.
    size: int  #: Size in bytes.
    ref: BlobRefLink  #: Reference to link.

    py_type: te.Literal['blob'] = Field(default='blob', alias='$type')

    @property
    def cid(self) -> 'CID':
        """Get CID."""
        from atproto.cid import CID

        return CID.decode(self.ref.link)

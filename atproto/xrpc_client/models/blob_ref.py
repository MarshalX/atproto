from atproto.cid import CID


class BlobRef:
    def __init__(self, blob_type: str, mime_type: str, ref: str, size: int):
        self.blob_type = blob_type
        self.mime_type = mime_type
        self.ref = ref
        self.size = size

    @property
    def cid(self) -> CID:
        return CID.decode(self.ref)

    @classmethod
    def from_dict(cls, data: dict) -> 'BlobRef':
        return cls(
            blob_type=data['$type'],
            mime_type=data['mimeType'],
            ref=data['ref']['$link'],
            size=int(data['size']),
        )

    def to_dict(self) -> dict:
        return {'$type': self.blob_type, 'mimeType': self.mime_type, 'size': self.size, 'ref': {'$link': self.ref}}

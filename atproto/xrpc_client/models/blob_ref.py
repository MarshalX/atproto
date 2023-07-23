from atproto.cid import CID


class BlobRef:
    def __init__(self, blob_type: str, mime_type: str, ref: str, size: int) -> None:
        self.blob_type = blob_type
        self.mime_type = mime_type
        self.ref = ref
        self.size = size

    @property
    def cid(self) -> CID:
        return CID.decode(self.ref)

    @classmethod
    def from_dict(cls, data: dict) -> 'BlobRef':
        ref = data['ref'].encode('base58btc') if isinstance(data['ref'], CID) else data['ref']['$link']

        return cls(
            blob_type=data['$type'],
            mime_type=data['mimeType'],
            ref=ref,
            size=int(data['size']),
        )

    def to_dict(self) -> dict:
        return {'$type': self.blob_type, 'mimeType': self.mime_type, 'size': self.size, 'ref': {'$link': self.ref}}

    def __str__(self) -> str:
        return str(self.to_dict())

    def __repr__(self) -> str:
        return f'BlobRef({self})'

import libipld


def multibase_to_bytes(data: str) -> bytes:
    _, data = libipld.decode_multibase(data)
    return data


def bytes_to_multibase(encoding: str, data: bytes) -> str:
    return libipld.encode_multibase(encoding, data)

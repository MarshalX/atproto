from cryptography.hazmat.primitives.asymmetric.ec import SECP256R1

from atproto_crypto.algs.base_alg import AlgBase


class P256(AlgBase):
    def __init__(self) -> None:
        super().__init__(SECP256R1())

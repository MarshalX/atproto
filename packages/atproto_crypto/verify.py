import typing as t
import warnings


def verify_signature(did_key: str, signing_input: t.Union[str, bytes], signature: t.Union[str, bytes]) -> bool:
    # TODO(MarshalX): implement
    warnings.warn(
        'verify_signature is not implemented yet. Do not trust to this signing_input',
        RuntimeWarning,
        stacklevel=0,
    )

    return True

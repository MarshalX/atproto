import typing as t
import warnings

from atproto_client import models


class _BackwardCompatibility:
    @staticmethod
    def _strong_ref_arg_backward_compatibility(
        uri: t.Optional[str] = None,
        cid: t.Optional[str] = None,
        subject: t.Optional[models.ComAtprotoRepoStrongRef.Main] = None,
    ) -> models.ComAtprotoRepoStrongRef.Main:
        """Temporary method for backward compatibility."""
        if subject:
            subject_obj = subject
            warnings.warn(
                'The `subject` argument is deprecated and will be removed soon!.',
                DeprecationWarning,
                stacklevel=2,
            )
        elif isinstance(uri, models.ComAtprotoRepoStrongRef.Main):
            warnings.warn(
                'The `uri` argument should be a string. Not ComAtprotoRepoStrongRef!', DeprecationWarning, stacklevel=2
            )
            subject_obj = uri
        else:
            if not cid or not uri:
                raise ValueError('URI and CID must be provided. It is temporary optional for backward compatibility.')

            subject_obj = models.ComAtprotoRepoStrongRef.Main(cid=cid, uri=uri)

        return subject_obj

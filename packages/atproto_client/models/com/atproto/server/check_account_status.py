##################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
##################################################################


from atproto_client.models import base


class Response(base.ResponseModelBase):
    """Output data model for :obj:`com.atproto.server.checkAccountStatus`."""

    activated: bool  #: Activated.
    expected_blobs: int  #: Expected blobs.
    imported_blobs: int  #: Imported blobs.
    indexed_records: int  #: Indexed records.
    private_state_values: int  #: Private state values.
    repo_blocks: int  #: Repo blocks.
    repo_commit: str  #: Repo commit.
    repo_rev: str  #: Repo rev.
    valid_did: bool  #: Valid did.

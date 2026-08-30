"""Alias of :mod:`atproto_client.models` as a real submodule of :mod:`atproto`.

``from atproto import models`` and ``from atproto.models import AppBskyFeedPost`` both resolve
to the very same module object.
"""

import sys
import typing as t

from atproto_client import models

if t.TYPE_CHECKING:
    from atproto_client.models import *  # noqa: F403

sys.modules[__name__] = models

# Allow downstream apps to identify themselves to upstream WAFs/edges.
# Generic `python-httpx/X.Y` User-Agents from cloud egress have been observed
# returning 403 from bsky.social (see bluesky-social/atproto#4764). Setting
# ATPROTO_USER_AGENT before importing this package overrides httpx's default
# User-Agent globally for this process. Leave unset to keep default behavior.
import os as _os

if _ua := _os.environ.get('ATPROTO_USER_AGENT', '').strip():
    import httpx._client

    httpx._client.USER_AGENT = _ua

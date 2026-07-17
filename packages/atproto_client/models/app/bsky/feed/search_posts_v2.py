#######################################################################
# THIS IS THE AUTO-GENERATED CODE. DON'T EDIT IT BY HANDS!
# Copyright (C) 2023-2026 Ilya (Marshal) <https://github.com/MarshalX>.
# This file is part of Python atproto SDK. Licenced under MIT.
#######################################################################


import typing as t

import typing_extensions as te
from pydantic import Field

from atproto_client.models import string_formats

if t.TYPE_CHECKING:
    from atproto_client import models
from atproto_client.models import base


class Params(base.ParamsModelBase):
    """Parameters model for :obj:`app.bsky.feed.searchPostsV2`."""

    all_time: t.Optional[bool] = None  #: Search the full index instead of the recent-post window.
    authors: t.Optional[t.List[string_formats.AtIdentifier]] = (
        None  #: Include posts by any of these authors. Handles are resolved to DIDs before searching.
    )
    cursor: t.Optional[str] = None  #: Optional pagination cursor.
    domains: t.Optional[t.List[str]] = None  #: Include posts that link to any of these domains.
    embedded_at_uris: t.Optional[t.List[string_formats.AtUri]] = None  #: Include posts that embed any of these AT URIs.
    exclude_authors: t.Optional[t.List[string_formats.AtIdentifier]] = (
        None  #: Exclude posts by any of these authors. Handles are resolved to DIDs before searching.
    )
    exclude_domains: t.Optional[t.List[str]] = None  #: Exclude posts that link to any of these domains.
    exclude_embedded_at_uris: t.Optional[t.List[string_formats.AtUri]] = (
        None  #: Exclude posts that embed any of these AT URIs.
    )
    exclude_hashtags: t.Optional[t.List[str]] = (
        None  #: Exclude posts tagged with any of these hashtags. Do not include the hash (#) prefix.
    )
    exclude_languages: t.Optional[t.List[string_formats.Language]] = (
        None  #: Exclude posts whose language matches any of these language codes.
    )
    exclude_mentions: t.Optional[t.List[string_formats.AtIdentifier]] = (
        None  #: Exclude posts that mention any of these accounts. Handles are resolved to DIDs before searching.
    )
    exclude_replies: t.Optional[bool] = None  #: Exclude replies from results. Mutually exclusive with repliesOnly.
    exclude_urls: t.Optional[t.List[string_formats.Uri]] = None  #: Exclude posts that link to any of these URLs.
    following: t.Optional[bool] = None  #: Include only posts from accounts followed by the viewer.
    has_media: t.Optional[bool] = None  #: Include only posts with media.
    has_video: t.Optional[bool] = None  #: Include only posts with video.
    hashtags: t.Optional[t.List[str]] = (
        None  #: Include posts tagged with any of these hashtags. Do not include the hash (#) prefix.
    )
    languages: t.Optional[t.List[string_formats.Language]] = (
        None  #: Include posts whose language matches any of these language codes.
    )
    limit: te.Annotated[t.Optional[int], Field(ge=1, le=100)] = None  #: Maximum number of results to return.
    mentions: t.Optional[t.List[string_formats.AtIdentifier]] = (
        None  #: Include posts that mention any of these accounts. Handles are resolved to DIDs before searching.
    )
    query: t.Optional[str] = None  #: Search query string. A query or at least one filter is required.
    query_language: t.Optional[
        t.Union[t.Literal['ja'], t.Literal['zh'], t.Literal['ko'], t.Literal['th'], t.Literal['ar'], str]
    ] = None  #: Language analyzer hint for the query text. If unset, the server auto-detects when possible.
    replies_only: t.Optional[bool] = None  #: Include only replies. Mutually exclusive with excludeReplies.
    reply_parent_uri: t.Optional[string_formats.AtUri] = None  #: Include only direct replies to this parent post URI.
    since: t.Optional[str] = (
        None  #: Include posts indexed at or after this timestamp. Can be a datetime, or just an ISO date (YYYY-MM-DD).
    )
    sort: t.Optional[t.Union[t.Literal['recent'], t.Literal['top'], str]] = (
        None  #: Ranking order for results. 'recent' sorts by recency; 'top' uses search ranking.
    )
    thread_root_uri: t.Optional[string_formats.AtUri] = (
        None  #: Include only posts in the thread rooted at this post URI.
    )
    until: t.Optional[str] = (
        None  #: Include posts indexed before this timestamp. Defaults to the current time. Can be a datetime, or just an ISO date (YYYY-MM-DD).
    )
    urls: t.Optional[t.List[string_formats.Uri]] = None  #: Include posts that link to any of these URLs.


class ParamsDict(t.TypedDict):
    all_time: te.NotRequired[t.Optional[bool]]  #: Search the full index instead of the recent-post window.
    authors: te.NotRequired[
        t.Optional[t.List[string_formats.AtIdentifier]]
    ]  #: Include posts by any of these authors. Handles are resolved to DIDs before searching.
    cursor: te.NotRequired[t.Optional[str]]  #: Optional pagination cursor.
    domains: te.NotRequired[t.Optional[t.List[str]]]  #: Include posts that link to any of these domains.
    embedded_at_uris: te.NotRequired[
        t.Optional[t.List[string_formats.AtUri]]
    ]  #: Include posts that embed any of these AT URIs.
    exclude_authors: te.NotRequired[
        t.Optional[t.List[string_formats.AtIdentifier]]
    ]  #: Exclude posts by any of these authors. Handles are resolved to DIDs before searching.
    exclude_domains: te.NotRequired[t.Optional[t.List[str]]]  #: Exclude posts that link to any of these domains.
    exclude_embedded_at_uris: te.NotRequired[
        t.Optional[t.List[string_formats.AtUri]]
    ]  #: Exclude posts that embed any of these AT URIs.
    exclude_hashtags: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Exclude posts tagged with any of these hashtags. Do not include the hash (#) prefix.
    exclude_languages: te.NotRequired[
        t.Optional[t.List[string_formats.Language]]
    ]  #: Exclude posts whose language matches any of these language codes.
    exclude_mentions: te.NotRequired[
        t.Optional[t.List[string_formats.AtIdentifier]]
    ]  #: Exclude posts that mention any of these accounts. Handles are resolved to DIDs before searching.
    exclude_replies: te.NotRequired[
        t.Optional[bool]
    ]  #: Exclude replies from results. Mutually exclusive with repliesOnly.
    exclude_urls: te.NotRequired[
        t.Optional[t.List[string_formats.Uri]]
    ]  #: Exclude posts that link to any of these URLs.
    following: te.NotRequired[t.Optional[bool]]  #: Include only posts from accounts followed by the viewer.
    has_media: te.NotRequired[t.Optional[bool]]  #: Include only posts with media.
    has_video: te.NotRequired[t.Optional[bool]]  #: Include only posts with video.
    hashtags: te.NotRequired[
        t.Optional[t.List[str]]
    ]  #: Include posts tagged with any of these hashtags. Do not include the hash (#) prefix.
    languages: te.NotRequired[
        t.Optional[t.List[string_formats.Language]]
    ]  #: Include posts whose language matches any of these language codes.
    limit: te.NotRequired[t.Optional[int]]  #: Maximum number of results to return.
    mentions: te.NotRequired[
        t.Optional[t.List[string_formats.AtIdentifier]]
    ]  #: Include posts that mention any of these accounts. Handles are resolved to DIDs before searching.
    query: te.NotRequired[t.Optional[str]]  #: Search query string. A query or at least one filter is required.
    query_language: te.NotRequired[
        t.Optional[t.Union[t.Literal['ja'], t.Literal['zh'], t.Literal['ko'], t.Literal['th'], t.Literal['ar'], str]]
    ]  #: Language analyzer hint for the query text. If unset, the server auto-detects when possible.
    replies_only: te.NotRequired[t.Optional[bool]]  #: Include only replies. Mutually exclusive with excludeReplies.
    reply_parent_uri: te.NotRequired[
        t.Optional[string_formats.AtUri]
    ]  #: Include only direct replies to this parent post URI.
    since: te.NotRequired[
        t.Optional[str]
    ]  #: Include posts indexed at or after this timestamp. Can be a datetime, or just an ISO date (YYYY-MM-DD).
    sort: te.NotRequired[
        t.Optional[t.Union[t.Literal['recent'], t.Literal['top'], str]]
    ]  #: Ranking order for results. 'recent' sorts by recency; 'top' uses search ranking.
    thread_root_uri: te.NotRequired[
        t.Optional[string_formats.AtUri]
    ]  #: Include only posts in the thread rooted at this post URI.
    until: te.NotRequired[
        t.Optional[str]
    ]  #: Include posts indexed before this timestamp. Defaults to the current time. Can be a datetime, or just an ISO date (YYYY-MM-DD).
    urls: te.NotRequired[t.Optional[t.List[string_formats.Uri]]]  #: Include posts that link to any of these URLs.


class Response(base.ResponseModelBase):
    """Output data model for :obj:`app.bsky.feed.searchPostsV2`."""

    posts: t.List['models.AppBskyFeedDefs.PostView']  #: Hydrated views of matching posts.
    cursor: t.Optional[str] = None  #: Cursor for the next page of results.
    detected_query_languages: t.Optional[
        t.List[t.Union[t.Literal['ja'], t.Literal['zh'], t.Literal['ko'], t.Literal['th'], t.Literal['ar'], str]]
    ] = None  #: Query languages detected for CJK, Thai, or Arabic text. Empty or omitted for other scripts.
    hits_total: t.Optional[int] = None  #: Estimated total number of matching hits. May be rounded or truncated.

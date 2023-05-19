"""Issue linking w/ plain-text autolinking, e.g. #42

Credit: https://github.com/ignatenkobrain/sphinxcontrib-issuetracker
License: BSD

Changes by Tony Narlock (2022-08-21):
- Type annotations

  mypy --strict, requires types-requests, types-docutils

  Python < 3.10 require typing-extensions
- TrackerConfig: Use dataclasses instead of typing.NamedTuple and hacking __new__
- app.warn (removed in 5.0) -> Use Sphinx Logging API

  https://www.sphinx-doc.org/en/master/extdev/logging.html#logging-api
- Add PendingIssueXRef

  Typing for tracker_config and precision
- Add IssueTrackerBuildEnvironment

  Subclassed / typed BuildEnvironment with .tracker_config
- Just GitHub (for demonstration)

LICENCE

Copyright (c) 2010, 2011, 2012 Sebastian Wiesner <lunaryorn@gmail.com>
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright
  notice, this list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright
  notice, this list of conditions and the following disclaimer in the
  documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
import dataclasses
import re
import sys
import time
import typing as t

import requests
from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.config import Config
from sphinx.environment import BuildEnvironment
from sphinx.transforms import SphinxTransform
from sphinx.util import logging

if t.TYPE_CHECKING:
    if sys.version_info >= (3, 10):
        from typing import TypeGuard
    else:
        from typing_extensions import TypeGuard

logger = logging.getLogger(__name__)

GITHUB_API_URL = "https://api.github.com/repos/{0.project}/issues/{1}"


class IssueTrackerBuildEnvironment(BuildEnvironment):
    tracker_config: "TrackerConfig"
    issuetracker_cache: "IssueTrackerCache"
    github_rate_limit: t.Tuple[float, bool]


class Issue(t.NamedTuple):
    id: str
    title: str
    url: str
    closed: bool


IssueTrackerCache = t.Dict[str, Issue]


@dataclasses.dataclass
class TrackerConfig:
    project: str
    url: str

    """
    Issue tracker configuration.
    This class provides configuration for trackers, and is passed as
    ``tracker_config`` arguments to callbacks of
    :event:`issuetracker-lookup-issue`.
    """

    def __post_init__(self) -> None:
        if self.url is not None:
            self.url = self.url.rstrip("/")

    @classmethod
    def from_sphinx_config(cls, config: Config) -> "TrackerConfig":
        """
        Get tracker configuration from ``config``.
        """
        project = config.issuetracker_project or config.project
        url = config.issuetracker_url
        return cls(project=project, url=url)


class PendingIssueXRef(pending_xref):
    tracker_config: TrackerConfig


class IssueReferences(SphinxTransform):
    default_priority = 999

    def apply(self) -> None:
        config = self.document.settings.env.config
        tracker_config = TrackerConfig.from_sphinx_config(config)
        issue_pattern = config.issuetracker_issue_pattern
        title_template = None
        if isinstance(issue_pattern, str):
            issue_pattern = re.compile(issue_pattern)
        for node in self.document.traverse(nodes.Text):
            parent = node.parent
            if isinstance(parent, (nodes.literal, nodes.FixedTextElement)):
                # ignore inline and block literal text
                continue
            if isinstance(parent, nodes.reference):
                continue
            text = str(node)
            new_nodes = []
            last_issue_ref_end = 0
            for match in issue_pattern.finditer(text):
                # catch invalid pattern with too many groups
                if len(match.groups()) != 1:
                    raise ValueError(
                        "issuetracker_issue_pattern must have " "exactly one group: {0!r}".format(match.groups())
                    )
                # extract the text between the last issue reference and the
                # current issue reference and put it into a new text node
                head = text[last_issue_ref_end : match.start()]
                if head:
                    new_nodes.append(nodes.Text(head))
                # adjust the position of the last issue reference in the
                # text
                last_issue_ref_end = match.end()
                # extract the issue text (including the leading dash)
                issuetext = match.group(0)
                # extract the issue number (excluding the leading dash)
                issue_id = match.group(1)
                # turn the issue reference into a reference node
                refnode = PendingIssueXRef()

                refnode["refdomain"] = None
                refnode["reftarget"] = issue_id
                refnode["reftype"] = "issue"
                refnode["trackerconfig"] = tracker_config
                reftitle = title_template or issuetext
                refnode.append(nodes.inline(issuetext, reftitle, classes=["xref", "issue"]))
                new_nodes.append(refnode)
            if not new_nodes:
                # no issue references were found, move on to the next node
                continue
            # extract the remaining text after the last issue reference, and
            # put it into a text node
            tail = text[last_issue_ref_end:]
            if tail:
                new_nodes.append(nodes.Text(tail))
            # find and remove the original node, and insert all new nodes
            # instead
            parent.replace(node, new_nodes)


def is_issuetracker_env(
    env: t.Any,
) -> "TypeGuard['IssueTrackerBuildEnvironment']":
    return hasattr(env, "issuetracker_cache") and env.issuetracker_cache is not None


def lookup_issue(app: Sphinx, tracker_config: TrackerConfig, issue_id: str) -> t.Optional[Issue]:
    """
    Lookup the given issue.
    The issue is first looked up in an internal cache.  If it is not found, the
    event ``issuetracker-lookup-issue`` is emitted.  The result of this
    invocation is then cached and returned.
    ``app`` is the sphinx application object.  ``tracker_config`` is the
    :class:`TrackerConfig` object representing the issue tracker configuration.
    ``issue_id`` is a string containing the issue id.
    Return a :class:`Issue` object for the issue with the given ``issue_id``,
    or ``None`` if the issue wasn't found.
    """
    env = app.env
    if is_issuetracker_env(env):
        cache: IssueTrackerCache = env.issuetracker_cache
        if issue_id not in cache:
            issue = app.emit_firstresult("issuetracker-lookup-issue", tracker_config, issue_id)
            cache[issue_id] = issue
        return cache[issue_id]
    return None


def lookup_issues(app: Sphinx, doctree: nodes.document) -> None:
    """
    Lookup issues found in the given ``doctree``.
    Each issue reference in the given ``doctree`` is looked up.  Each lookup
    result is cached by mapping the referenced issue id to the looked up
    :class:`Issue` object (an existing issue) or ``None`` (a missing issue).
    The cache is available at ``app.env.issuetracker_cache`` and is pickled
    along with the environment.
    """
    for node in doctree.traverse(PendingIssueXRef):
        if node["reftype"] == "issue":
            lookup_issue(app, node["trackerconfig"], node["reftarget"])


def make_issue_reference(issue: Issue, content_node: nodes.inline) -> nodes.reference:
    """
    Create a reference node for the given issue.
    ``content_node`` is a docutils node which is supposed to be added as
    content of the created reference.  ``issue`` is the :class:`Issue` which
    the reference shall point to.
    Return a :class:`docutils.nodes.reference` for the issue.
    """
    reference = nodes.reference()
    reference["refuri"] = issue.url
    if issue.title:
        reference["reftitle"] = issue.title
    if issue.closed:
        content_node["classes"].append("closed")
    reference.append(content_node)
    return reference


def resolve_issue_reference(
    app: Sphinx, env: BuildEnvironment, node: PendingIssueXRef, contnode: nodes.inline
) -> t.Optional[nodes.reference]:
    """
    Resolve an issue reference and turn it into a real reference to the
    corresponding issue.
    ``app`` and ``env`` are the Sphinx application and environment
    respectively.  ``node`` is a ``pending_xref`` node representing the missing
    reference.  It is expected to have the following attributes:
    - ``reftype``: The reference type
    - ``trackerconfig``: The :class:`TrackerConfig`` to use for this node
    - ``reftarget``: The issue id
    - ``classes``: The node classes
    References with a ``reftype`` other than ``'issue'`` are skipped by
    returning ``None``.  Otherwise the new node is returned.
    If the referenced issue was found, a real reference to this issue is
    returned.  The text of this reference is formatted with the :class:`Issue`
    object available in the ``issue`` key.  The reference title is set to the
    issue title.  If the issue is closed, the class ``closed`` is added to the
    new content node.
    Otherwise, if the issue was not found, the content node is returned.
    """
    if node["reftype"] != "issue":
        return None

    issue = lookup_issue(app, node["trackerconfig"], node["reftarget"])
    if issue is None:
        return contnode
    else:
        classes = contnode["classes"]
        conttext = str(contnode[0])
        formatted_conttext = nodes.Text(conttext.format(issue=issue))
        formatted_contnode = nodes.inline(conttext, formatted_conttext, classes=classes)
        assert issue is not None
        return make_issue_reference(issue, formatted_contnode)
    return None


def init_cache(app: Sphinx) -> None:
    if not hasattr(app.env, "issuetracker_cache"):
        app.env.issuetracker_cache: "IssueTrackerCache" = {}  # type: ignore
    return None


def check_project_with_username(tracker_config: TrackerConfig) -> None:
    if "/" not in tracker_config.project:
        raise ValueError("username missing in project name: {0.project}".format(tracker_config))


HEADERS = {"User-Agent": "sphinxcontrib-issuetracker v{0}".format("1.0")}


def get(app: Sphinx, url: str) -> t.Optional[requests.Response]:
    """
    Get a response from the given ``url``.
    ``url`` is a string containing the URL to request via GET. ``app`` is the
    Sphinx application object.
    Return the :class:`~requests.Response` object on status code 200, or
    ``None`` otherwise. If the status code is not 200 or 404, a warning is
    emitted via ``app``.
    """
    response = requests.get(url, headers=HEADERS)
    if response.status_code == requests.codes.ok:
        return response
    elif response.status_code != requests.codes.not_found:
        msg = "GET {0.url} failed with code {0.status_code}"
        logger.warning(msg.format(response))

    return None


def lookup_github_issue(app: Sphinx, tracker_config: TrackerConfig, issue_id: str) -> t.Optional[Issue]:
    check_project_with_username(tracker_config)

    env = app.env
    if is_issuetracker_env(env):
        # Get rate limit information from the environment
        timestamp, limit_hit = getattr(env, "github_rate_limit", (0, False))

        if limit_hit and time.time() - timestamp > 3600:
            # Github limits applications hourly
            limit_hit = False

        if not limit_hit:
            url = GITHUB_API_URL.format(tracker_config, issue_id)
            response = get(app, url)
            if response:
                rate_remaining = response.headers.get("X-RateLimit-Remaining")
                assert rate_remaining is not None
                if rate_remaining.isdigit() and int(rate_remaining) == 0:
                    logger.warning("Github rate limit hit")
                    env.github_rate_limit = (time.time(), True)
                issue = response.json()
                closed = issue["state"] == "closed"
                return Issue(
                    id=issue_id,
                    title=issue["title"],
                    closed=closed,
                    url=issue["html_url"],
                )
        else:
            logger.warning("Github rate limit exceeded, not resolving issue {0}".format(issue_id))
    return None


BUILTIN_ISSUE_TRACKERS: t.Dict[str, t.Any] = {
    "github": lookup_github_issue,
}


def init_transformer(app: Sphinx) -> None:
    if app.config.issuetracker_plaintext_issues:
        app.add_transform(IssueReferences)


def connect_builtin_tracker(app: Sphinx) -> None:
    if app.config.issuetracker:
        tracker = BUILTIN_ISSUE_TRACKERS[app.config.issuetracker.lower()]
        app.connect(str("issuetracker-lookup-issue"), tracker)


def setup(app: Sphinx) -> t.Dict[str, t.Any]:
    app.add_config_value("mybase", "https://github.com/cihai/unihan-etl", "env")
    app.add_event(str("issuetracker-lookup-issue"))
    app.connect(str("builder-inited"), connect_builtin_tracker)
    app.add_config_value("issuetracker", None, "env")
    app.add_config_value("issuetracker_project", None, "env")
    app.add_config_value("issuetracker_url", None, "env")
    # configuration specific to plaintext issue references
    app.add_config_value("issuetracker_plaintext_issues", True, "env")
    app.add_config_value(
        "issuetracker_issue_pattern",
        re.compile(
            r"#(\d+)",
        ),
        "env",
    )
    app.add_config_value("issuetracker_title_template", None, "env")
    app.connect(str("builder-inited"), init_cache)
    app.connect(str("builder-inited"), init_transformer)
    app.connect(str("doctree-read"), lookup_issues)
    app.connect(str("missing-reference"), resolve_issue_reference)
    return {
        "version": "1.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

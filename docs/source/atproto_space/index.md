# Spaces

Client for [Spaces](https://github.com/bluesky-social/proposals/tree/main/0016-permissioned-data), the permissioned data of the AT Protocol: records with an access perimeter, such as bookmarks, drafts, private posts and group forums. This package requests and renews space credentials, sends each request to the server that holds the data, and verifies what comes back.

:::{warning}
Spaces are in alpha. The protocol is not final, and the classes, the methods and the lexicons behind them can change with it in any release.
:::

[SpaceClient](#atproto_space.SpaceClient) / [AsyncSpaceClient](#atproto_space.AsyncSpaceClient)
: A space as one account sees it. Reads the space and writes the repo of the account in it.

[SpaceReader](#atproto_space.SpaceReader) / [AsyncSpaceReader](#atproto_space.AsyncSpaceReader)
: A space read with space credentials only, for a service that keeps its own copy of spaces.

[SpaceManager](#atproto_space.SpaceManager) / [AsyncSpaceManager](#atproto_space.AsyncSpaceManager)
: The policy, the writers and the members of a space, for its authority.

[SpaceType](#atproto_space.SpaceType)
: A space type as its lexicon declares it: the type of the key and the record collections.

:::{tip}
For how to use these, covering scopes, records, blobs, managing a space and syncing one, see the [Spaces guide](../guides/spaces.md).
:::

```{eval-rst}
.. automodule:: atproto_space
   :members:
   :inherited-members:
```

## Submodules

The clients are built from these. You need them directly only when you verify space data that you fetched yourself.

```{toctree}
:maxdepth: 4

tokens
mac
commit
repo_archive
```

# Spaces

Records with an access perimeter, kept apart from the public repository. For the prose on scopes, members, verification and syncing a space, see [Spaces](../guides/spaces.md).

:::{warning}
Spaces are in alpha. The example needs a PDS that supports them and a space type that is published as a lexicon, and it can change with the protocol.
:::

## Keep private bookmarks

A personal space is read only by its owner and the applications the owner authorized. The space is created on the first run, and the OAuth scope asks for nothing but the bookmarks of the account.

```{literalinclude} ../../../examples/spaces/bookmarks.py
:language: python
:caption: examples/spaces/bookmarks.py
```

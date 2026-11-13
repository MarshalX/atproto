import typing_extensions as te

from atproto_oauth.scopes.scope_permissions import ScopePermissions


class ScopePermissionsTransition(ScopePermissions):
    """Permission checker with transition scope support.

    Transition scopes are legacy grants from the pre-scoped OAuth era:

    - ``transition:generic``: all repo, all blob, all non-chat.bsky RPC
    - ``transition:chat.bsky``: all chat.bsky.* RPC methods
    - ``transition:email``: read access to account email
    """

    @property
    def has_transition_generic(self) -> bool:
        return self.scopes.has('transition:generic')

    @property
    def has_transition_email(self) -> bool:
        return self.scopes.has('transition:email')

    @property
    def has_transition_chat_bsky(self) -> bool:
        return self.scopes.has('transition:chat.bsky')

    @te.override
    def allows_account(self, attr: str, action: str) -> bool:
        if attr == 'email' and action == 'read' and self.has_transition_email:
            return True

        return super().allows_account(attr, action)

    @te.override
    def allows_blob(self, mime: str) -> bool:
        if self.has_transition_generic:
            return True

        return super().allows_blob(mime)

    @te.override
    def allows_repo(self, collection: str, action: str) -> bool:
        if self.has_transition_generic:
            return True

        return super().allows_repo(collection, action)

    @te.override
    def allows_rpc(self, lxm: str, aud: str) -> bool:
        if self.has_transition_generic and lxm == '*':
            return True

        if self.has_transition_generic and not lxm.startswith('chat.bsky.'):
            return True

        if self.has_transition_chat_bsky and lxm.startswith('chat.bsky.'):
            return True

        return super().allows_rpc(lxm, aud)

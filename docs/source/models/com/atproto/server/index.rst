com.atproto.server
==================

Accounts, sessions, invites, and app passwords.

.. automodule:: atproto_client.models.com.atproto.server
   :members:
   :show-inheritance:
   :undoc-members:

.. grid:: 1 2 2 3
   :gutter: 3

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` activateAccount
      :link: /models/com/atproto/server/activateAccount
      :link-type: doc

      Activates a currently deactivated account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` checkAccountStatus
      :link: /models/com/atproto/server/checkAccountStatus
      :link-type: doc

      Returns the status of an account, especially as pertaining to import or recovery.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` confirmEmail
      :link: /models/com/atproto/server/confirmEmail
      :link-type: doc

      Confirm an email using a token from com.atproto.server.requestEmailConfirmation.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createAccount
      :link: /models/com/atproto/server/createAccount
      :link-type: doc

      Create an account.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createAppPassword
      :link: /models/com/atproto/server/createAppPassword
      :link-type: doc

      Create an App Password.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createInviteCode
      :link: /models/com/atproto/server/createInviteCode
      :link-type: doc

      Create an invite code.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createInviteCodes
      :link: /models/com/atproto/server/createInviteCodes
      :link-type: doc

      Create invite codes.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` createSession
      :link: /models/com/atproto/server/createSession
      :link-type: doc

      Create an authentication session.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` deactivateAccount
      :link: /models/com/atproto/server/deactivateAccount
      :link-type: doc

      Deactivates a currently active account.

   .. grid-item-card:: :octicon:`code;1em;sd-mr-1` defs
      :link: /models/com/atproto/server/defs
      :link-type: doc

      Shared type definitions.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` deleteAccount
      :link: /models/com/atproto/server/deleteAccount
      :link-type: doc

      Delete an actor's account with a token and password.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` deleteSession
      :link: /models/com/atproto/server/deleteSession
      :link-type: doc

      Delete the current session.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` describeServer
      :link: /models/com/atproto/server/describeServer
      :link-type: doc

      Describes the server's account creation requirements and capabilities.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getAccountInviteCodes
      :link: /models/com/atproto/server/getAccountInviteCodes
      :link-type: doc

      Get all invite codes for the current account.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getServiceAuth
      :link: /models/com/atproto/server/getServiceAuth
      :link-type: doc

      Get a signed token on behalf of the requesting DID for the requested service.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` getSession
      :link: /models/com/atproto/server/getSession
      :link-type: doc

      Get information about the current auth session.

   .. grid-item-card:: :octicon:`search;1em;sd-mr-1` listAppPasswords
      :link: /models/com/atproto/server/listAppPasswords
      :link-type: doc

      List all App Passwords.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` refreshSession
      :link: /models/com/atproto/server/refreshSession
      :link-type: doc

      Refresh an authentication session.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` requestAccountDelete
      :link: /models/com/atproto/server/requestAccountDelete
      :link-type: doc

      Initiate a user account deletion via email.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` requestEmailConfirmation
      :link: /models/com/atproto/server/requestEmailConfirmation
      :link-type: doc

      Request an email with a code to confirm ownership of email.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` requestEmailUpdate
      :link: /models/com/atproto/server/requestEmailUpdate
      :link-type: doc

      Request a token in order to update email.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` requestPasswordReset
      :link: /models/com/atproto/server/requestPasswordReset
      :link-type: doc

      Initiate a user account password reset via email.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` reserveSigningKey
      :link: /models/com/atproto/server/reserveSigningKey
      :link-type: doc

      Reserve a repo signing key, for use with account creation.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` resetPassword
      :link: /models/com/atproto/server/resetPassword
      :link-type: doc

      Reset a user account password using a token.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` revokeAppPassword
      :link: /models/com/atproto/server/revokeAppPassword
      :link-type: doc

      Revoke an App Password by name.

   .. grid-item-card:: :octicon:`zap;1em;sd-mr-1` updateEmail
      :link: /models/com/atproto/server/updateEmail
      :link-type: doc

      Update an account's email.

.. toctree::
   :hidden:
   :maxdepth: 1

   activateAccount </models/com/atproto/server/activateAccount>
   checkAccountStatus </models/com/atproto/server/checkAccountStatus>
   confirmEmail </models/com/atproto/server/confirmEmail>
   createAccount </models/com/atproto/server/createAccount>
   createAppPassword </models/com/atproto/server/createAppPassword>
   createInviteCode </models/com/atproto/server/createInviteCode>
   createInviteCodes </models/com/atproto/server/createInviteCodes>
   createSession </models/com/atproto/server/createSession>
   deactivateAccount </models/com/atproto/server/deactivateAccount>
   defs </models/com/atproto/server/defs>
   deleteAccount </models/com/atproto/server/deleteAccount>
   deleteSession </models/com/atproto/server/deleteSession>
   describeServer </models/com/atproto/server/describeServer>
   getAccountInviteCodes </models/com/atproto/server/getAccountInviteCodes>
   getServiceAuth </models/com/atproto/server/getServiceAuth>
   getSession </models/com/atproto/server/getSession>
   listAppPasswords </models/com/atproto/server/listAppPasswords>
   refreshSession </models/com/atproto/server/refreshSession>
   requestAccountDelete </models/com/atproto/server/requestAccountDelete>
   requestEmailConfirmation </models/com/atproto/server/requestEmailConfirmation>
   requestEmailUpdate </models/com/atproto/server/requestEmailUpdate>
   requestPasswordReset </models/com/atproto/server/requestPasswordReset>
   reserveSigningKey </models/com/atproto/server/reserveSigningKey>
   resetPassword </models/com/atproto/server/resetPassword>
   revokeAppPassword </models/com/atproto/server/revokeAppPassword>
   updateEmail </models/com/atproto/server/updateEmail>

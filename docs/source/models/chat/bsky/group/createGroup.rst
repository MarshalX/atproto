chat.bsky.group.createGroup
===========================

Creates a group convo, specifying the members to be added to it. Unlike getConvoForMembers, this isn't idempotent. It will create new groups even if the membership is identical to pre-existing groups. Will create 'request' membership for all members, except the owner who is 'accepted'.

.. automodule:: atproto_client.models.chat.bsky.group.create_group
   :members:
   :show-inheritance:
   :undoc-members:

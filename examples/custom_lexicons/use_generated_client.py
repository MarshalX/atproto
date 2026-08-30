"""Use a package generated from custom lexicons.

Generate it first, from this directory:

    atp gen --lexicon-dir ./lexicons custom --output-dir ./statusphere --package statusphere
"""

from atproto import Client, models

# The generated package. Importing it registers its record types for $type resolution.
from statusphere import models as statusphere_models
from statusphere.client import StatusphereClient, attach_namespaces

USERNAME = 'example.com'
PASSWORD = 'hunter2'  # noqa: S105 never hardcode your password in a real application


def with_generated_client() -> None:
    # StatusphereClient is a subclass of the SDK Client, so it keeps app, com, chat and the rest
    client = StatusphereClient()
    client.login(USERNAME, PASSWORD)

    # the SDK's own namespaces still work
    print(client.app.bsky.actor.get_profile({'actor': client.me.did}).display_name)

    # and so do yours
    print(client.xyz.statusphere.get_statuses({'limit': 10}))

    # records of your own lexicons get the same sugar as the built-in ones
    status = statusphere_models.XyzStatusphereStatus.Record(
        status='👍',
        created_at=client.get_current_time_iso(),
    )
    created = client.xyz.statusphere.status.create(client.me.did, status)
    print(created.uri)


def with_existing_client() -> None:
    # Already have a client? Graft the namespaces onto it instead of switching classes.
    client = Client()
    client.login(USERNAME, PASSWORD)

    attach_namespaces(client)
    print(client.xyz.statusphere.get_statuses({'limit': 10}))


def resolve_a_custom_record() -> None:
    # $type resolution reaches into the generated package, so a custom record nested in an
    # SDK model deserializes to your class instead of degrading to DotDict.
    record = models.get_or_create(
        {'$type': 'xyz.statusphere.status', 'status': '👍', 'createdAt': '2026-01-01T00:00:00Z'},
        None,
        strict=False,
    )
    print(type(record), record.status)


if __name__ == '__main__':
    with_generated_client()

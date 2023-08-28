from datetime import datetime, timezone
from time import sleep

from atproto import Client

# how often we should check for new notifications
FETCH_NOTIFICATIONS_DELAY_SEC = 3


def main():
    client = Client()
    client.login('my-handle', 'my-password')

    # fetch new notifications
    while True:
        # save the time in UTC when we fetch notifications
        last_seen_at = datetime.now(timezone.utc).isoformat()

        response = client.app.bsky.notification.list_notifications()
        for notification in response.notifications:
            if not notification.isRead:
                print(f'Got new notification! Type: {notification.reason}; from: {notification.author.did}')
                # example: "Got new notification! Type: like; from: did:plc:hlorqa2iqfooopmyzvb4byaz"

        # mark notifications as processed (isRead=True)
        client.app.bsky.notification.update_seen({'seenAt': last_seen_at})
        print('Successfully process notification. Last seen at:', last_seen_at)

        sleep(FETCH_NOTIFICATIONS_DELAY_SEC)


if __name__ == '__main__':
    main()

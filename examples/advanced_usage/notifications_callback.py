import asyncio
import typing as t

from atproto import AsyncClient, models

# how often we should check for new notifications
FETCH_NOTIFICATIONS_DELAY_SEC = 3.0

Notification = models.AppBskyNotificationListNotifications.Notification


async def main() -> None:
    async_client = AsyncClient()
    await async_client.login('my-handle', 'my-password')

    async def on_notification_callback(notification: Notification) -> None:
        print(f'Got new notification! Type: {notification.reason}; from: {notification.author.did}')
        # example: "Got new notification! Type: like; from: did:plc:hlorqa2iqfooopmyzvb4byaz"

    async def listen_for_notifications(
        on_notification: t.Callable[[Notification], t.Coroutine[t.Any, t.Any, None]],
    ) -> None:
        print('Start listening for notifications...')
        while True:
            # save the time in UTC when we fetch notifications
            last_seen_at = async_client.get_current_time_iso()

            # fetch new notifications
            response = await async_client.app.bsky.notification.list_notifications()

            # create a task list to run callbacks concurrently
            on_notification_tasks = []
            for notification in response.notifications:
                if not notification.is_read:
                    on_notification_tasks.append(on_notification(notification))

            # run callback on each notification
            await asyncio.gather(*on_notification_tasks)

            # mark notifications as processed (isRead=True)
            await async_client.app.bsky.notification.update_seen({'seen_at': last_seen_at})
            print('Successfully process notification. Last seen at:', last_seen_at)

            await asyncio.sleep(FETCH_NOTIFICATIONS_DELAY_SEC)

    # run our notification listener and register the callback on notification
    await asyncio.ensure_future(listen_for_notifications(on_notification_callback))


if __name__ == '__main__':
    # use run() for a higher Python version
    asyncio.get_event_loop().run_until_complete(main())

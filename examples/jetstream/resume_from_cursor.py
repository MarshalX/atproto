"""Persist the cursor so a restart resumes where the previous run stopped."""

import os
import typing as t
from pathlib import Path

from atproto import JetstreamClient, jetstream_models, models

_CURSOR_FILE = Path('jetstream.cursor')

#: Saving on every event would hammer the disk
_SAVE_EVERY = 100


def load_cursor() -> t.Optional[int]:
    try:
        return int(_CURSOR_FILE.read_text())
    except (OSError, ValueError):
        # missing or truncated by a crash; start from the live tip
        return None


def save_cursor(cursor: int) -> None:
    # write to a temporary file and rename, so a crash cannot leave a half-written cursor
    tmp_file = _CURSOR_FILE.with_suffix('.tmp')
    tmp_file.write_text(str(cursor))
    os.replace(tmp_file, _CURSOR_FILE)


params: models.NetworkBskyJetstreamSubscribeEvents.ParamsDict = {'kinds': ['commit']}

cursor = load_cursor()
if cursor is not None:
    params['cursor'] = cursor

client = JetstreamClient(params=params)
processed = 0


def on_message_handler(event: jetstream_models.SubscribeEventsMessage) -> None:
    global processed

    if isinstance(event, models.NetworkBskyJetstreamSubscribeEvents.Info):
        return

    print(event.seq, event.did)

    processed += 1
    if processed % _SAVE_EVERY == 0 and client.cursor is not None:
        save_cursor(client.cursor)


client.start(on_message_handler)

import threading
import time

from atproto.firehose import FirehoseSubscribeReposClient, parse_subscribe_repos_message

_STOP_AFTER_SECONDS = 3

client = FirehoseSubscribeReposClient()


def on_message_handler(message):
    print(message.header, parse_subscribe_repos_message(message))


def _stop_after_n_sec():
    time.sleep(_STOP_AFTER_SECONDS)
    client.stop()


# run our sleep functions in another thread
threading.Thread(target=_stop_after_n_sec).start()

# run the client for N seconds
client.start(on_message_handler)

print(f'Successfully stopped after {_STOP_AFTER_SECONDS} seconds!')

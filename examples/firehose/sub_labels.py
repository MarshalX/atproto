from atproto import FirehoseSubscribeLabelsClient, firehose_models, models, parse_subscribe_labels_message

client = FirehoseSubscribeLabelsClient()


def on_message_handler(message: firehose_models.MessageFrame) -> None:
    labels_message = parse_subscribe_labels_message(message)
    if not isinstance(labels_message, models.ComAtprotoLabelSubscribeLabels.Labels):
        return

    for label in labels_message.labels:
        neg = '(NEG)' if label.neg else ''
        print(f'[{label.cts}] ({label.src}) {label.uri} => {label.val} {neg}')


client.start(on_message_handler)

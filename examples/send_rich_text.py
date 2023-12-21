from atproto import Client, client_utils

# To send links as "link card" or "quote post" look at the advanced_usage/send_embed.py example.
# There is a more advanced way to send rich text without helper class in the advanced_usage/send_rich_text.py example.


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    text_builder = client_utils.TextBuilder()
    text_builder.tag('This is a rich message. ', 'atproto')
    text_builder.text('I can mention ')
    text_builder.mention('account', 'did:plc:kvwvcn5iqfooopmyzvb4qzba')
    text_builder.text(' and add clickable ')
    text_builder.link('link', 'https://atproto.blue/')

    # You can pass instance of TextBuilder instead of str to the "text" argument.
    client.send_post(text_builder)  # same with send_image method

    # Same with chaining:
    client.send_post(client_utils.TextBuilder().text('Test msg using ').link('Python SDK', 'https://atproto.blue/'))


if __name__ == '__main__':
    main()

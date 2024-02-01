import re
import typing as t

from atproto import Client, models


def extract_url_byte_positions(text: str, *, encoding: str = 'UTF-8') -> t.List[t.Tuple[str, int, int]]:
    """This function will detect any links beginning with http or https."""
    encoded_text = text.encode(encoding)

    # Adjusted URL matching pattern
    pattern = rb'https?://[^ \n\r\t]*'

    matches = re.finditer(pattern, encoded_text)
    url_byte_positions = []

    for match in matches:
        url_bytes = match.group(0)
        url = url_bytes.decode(encoding)
        url_byte_positions.append((url, match.start(), match.end()))

    return url_byte_positions


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    # AT requires URL to include http or https when creating the facet
    text = 'Example post with automatic link detection https://github.com/MarshalX/atproto and http://atproto.blue'

    # Determine locations of URLs in the post's text
    url_positions = extract_url_byte_positions(text)
    facets = []

    for link_data in url_positions:
        uri, byte_start, byte_end = link_data
        facets.append(
            models.AppBskyRichtextFacet.Main(
                features=[models.AppBskyRichtextFacet.Link(uri=uri)],
                index=models.AppBskyRichtextFacet.ByteSlice(byte_start=byte_start, byte_end=byte_end),
            )
        )

    client.send_post(text, facets=facets)


if __name__ == '__main__':
    main()

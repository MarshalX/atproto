import re
import typing as t

import httpx
from atproto import Client, models

_META_PATTERN = re.compile(r'<meta property="og:.*?>')
_CONTENT_PATTERN = re.compile(r'<meta[^>]+content="([^"]+)"')


def _find_tag(og_tags: t.List[str], search_tag: str) -> t.Optional[str]:
    for tag in og_tags:
        if search_tag in tag:
            return tag

    return None


def _get_tag_content(tag: str) -> t.Optional[str]:
    match = _CONTENT_PATTERN.match(tag)
    if match:
        return match.group(1)

    return None


def _get_og_tag_value(og_tags: t.List[str], tag_name: str) -> t.Optional[str]:
    tag = _find_tag(og_tags, tag_name)
    if tag:
        return _get_tag_content(tag)

    return None


def get_og_tags(url: str) -> t.Tuple[t.Optional[str], t.Optional[str], t.Optional[str]]:
    response = httpx.get(url)
    response.raise_for_status()

    og_tags = _META_PATTERN.findall(response.text)

    og_image = _get_og_tag_value(og_tags, 'og:image')
    og_title = _get_og_tag_value(og_tags, 'og:title')
    og_description = _get_og_tag_value(og_tags, 'og:description')

    return og_image, og_title, og_description


def main() -> None:
    client = Client()
    client.login('my-handle', 'my-password')

    url = 'https://github.com/MarshalX/atproto'
    text = 'Example post with embed external resource (link card) with Open Graph Protocol (OGP) tags from the website'

    img_url, title, description = get_og_tags(url)
    if title is None or description is None:
        raise ValueError('Required Open Graph Protocol (OGP) tags not found')

    thumb_blob = None
    if img_url:
        # Download image from og:image url and upload it as a blob
        img_data = httpx.get(img_url).content
        thumb_blob = client.upload_blob(img_data).blob

    # AppBskyEmbedExternal is the same as "link card" in the app
    embed_external = models.AppBskyEmbedExternal.Main(
        external=models.AppBskyEmbedExternal.External(title=title, description=description, uri=url, thumb=thumb_blob)
    )
    client.send_post(text=text, embed=embed_external)


if __name__ == '__main__':
    main()

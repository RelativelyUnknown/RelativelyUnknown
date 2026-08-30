#!/usr/bin/env python3
"""Vendor the avatars for [[favourites.items]] into avatars.json.

Same reason as the icons: an SVG that GitHub serves through <img> can't load
anything from the network, so the picture has to be inside the file. Each one
is fetched from github.com/<owner>.png?size=96 - GitHub resizes it server
side, so there is nothing to scale here - and stored base64, ready to drop
into an SVG as a data: URI.

An owner already in avatars.json is left alone, and with nothing missing this
doesn't touch the network at all. `--refresh` re-fetches everything, which is
how you pick up an avatar somebody has changed.

A fetch that fails is not fatal: the card falls back to drawing the owner's
initial, so a rate limit or a deleted account costs a picture, not a block.
Nor is a fetch that succeeds trusted blindly - what came back is logged with
its size and dimensions, and GitHub's generic stand-in picture is refused by
content rather than committed as if it were somebody's avatar.

Usage:  python3 build_avatars.py [--refresh]
"""
import base64
import hashlib
import json
import pathlib
import struct
import sys
import urllib.error
import urllib.request

from config import load

HERE = pathlib.Path(__file__).resolve().parent
AVATARS = HERE / 'avatars.json'
SIZE = 96
LIMIT = 60_000          # bytes; an avatar this big means something is wrong
AGENT = 'profile-readme-bot'

MAGIC = {b'\x89PNG\r\n\x1a\n': 'image/png', b'\xff\xd8\xff': 'image/jpeg'}

# GitHub hands out one generic picture for anything it cannot resolve to a
# real account - the same 5065 bytes for a name that does not exist as for a
# name that does, on the avatars.githubusercontent.com/<login> path. Vendoring
# it would look like a success and render as a stranger's placeholder, so it is
# refused by content. Pinned deliberately narrowly: if GitHub ever changes that
# asset this simply stops matching, which is the old behaviour back. It can
# never reject a real avatar.
GENERIC = '2ae73e12cb1e9989929920c4e9da0b02'


def digest(blob):
    return hashlib.sha256(blob).hexdigest()[:32]


def dimensions(blob):
    """(width, height) from a PNG or JPEG header, so the log says what was
    actually vendored rather than just how many bytes it was."""
    if blob.startswith(b'\x89PNG\r\n\x1a\n'):
        return struct.unpack('>II', blob[16:24])
    if blob.startswith(b'\xff\xd8\xff'):
        i = 2
        while i < len(blob) - 9:
            if blob[i] != 0xFF:
                i += 1
                continue
            marker = blob[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack('>HH', blob[i + 5:i + 9])
                return width, height
            i += 2 + struct.unpack('>H', blob[i + 2:i + 4])[0]
    return None


def owners(cfg):
    """The owner of every favourite, in the order they are listed."""
    out = []
    for item in cfg['favourites']['items']:
        owner = item.get('owner') or url_parts(item.get('url', ''))[0]
        if owner and owner not in out:
            out.append(owner)
    return out


def url_parts(url):
    """('pydantic', 'pydantic') out of https://github.com/pydantic/pydantic."""
    tail = url.split('github.com/', 1)[-1].strip('/')
    bits = [b for b in tail.split('/') if b]
    return (bits + [None, None])[:2]


def mime(blob):
    for magic, kind in MAGIC.items():
        if blob.startswith(magic):
            return kind
    return None


def fetch(owner):
    """github.com/<login>.png is the endpoint that actually resolves a login;
    it redirects to the numeric avatars.githubusercontent.com/u/<id> URL and
    GitHub does the resizing. Do not be tempted by
    avatars.githubusercontent.com/<login> - that one answers for every name,
    real or not, with the same generic picture."""
    url = f'https://github.com/{owner}.png?size={SIZE}'
    request = urllib.request.Request(url, headers={'User-Agent': AGENT})
    with urllib.request.urlopen(request, timeout=30) as resp:
        return resp.read(LIMIT + 1)


def vendor(owner, blob):
    """The checks between "something came back" and "put it in the file"."""
    if len(blob) > LIMIT:
        print(f'  {owner}: over {LIMIT} bytes, skipping')
        return None
    kind = mime(blob)
    if not kind:
        print(f'  {owner}: not a PNG or JPEG, skipping')
        return None
    if digest(blob) == GENERIC:
        print(f'  {owner}: this is GitHub\'s generic picture, not {owner}\'s - '
              f'skipping rather than passing it off as an avatar')
        return None
    size = dimensions(blob)
    print(f'  {owner}: {kind}, {len(blob)} bytes'
          + (f', {size[0]}x{size[1]}' if size else ''))
    return {'mime': kind, 'data': base64.b64encode(blob).decode()}


def main(refresh=False):
    cfg = load()
    have = json.loads(AVATARS.read_text()) if AVATARS.exists() else {}
    names = owners(cfg)
    missing = names if refresh else [n for n in names if n not in have]

    added = 0
    for owner in missing:
        try:
            blob = fetch(owner)
        except (urllib.error.URLError, OSError) as exc:
            print(f'  {owner}: {exc}, skipping (the card draws an initial instead)')
            continue
        picture = vendor(owner, blob)
        if picture:
            have[owner] = picture
            added += 1

    # Dropping anyone no longer listed happens whether or not there was
    # anything to fetch, so removing a favourite takes its picture with it.
    kept = {k: v for k, v in have.items() if k in names}
    dropped = sorted(set(have) - set(kept))
    if dropped:
        print(f'  dropped {", ".join(dropped)}, no longer a favourite')
    if added or dropped:
        AVATARS.write_text(json.dumps(kept))
    if not missing:
        print(f'{len(kept)} avatars already vendored, nothing to fetch')
    else:
        print(f'{added} added, {len(kept)} avatars in avatars.json')


if __name__ == '__main__':
    main(refresh='--refresh' in sys.argv)

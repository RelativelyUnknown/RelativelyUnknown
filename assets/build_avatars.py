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

Usage:  python3 build_avatars.py [--refresh]
"""
import base64
import json
import pathlib
import sys
import urllib.error
import urllib.request

from config import load

HERE = pathlib.Path(__file__).resolve().parent
AVATARS = HERE / 'avatars.json'
SIZE = 96
LIMIT = 60_000          # bytes; an avatar this big means something is wrong

MAGIC = {b'\x89PNG\r\n\x1a\n': 'image/png', b'\xff\xd8\xff': 'image/jpeg'}


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
    url = f'https://github.com/{owner}.png?size={SIZE}'
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read(LIMIT + 1)


def main(refresh=False):
    cfg = load()
    have = json.loads(AVATARS.read_text()) if AVATARS.exists() else {}
    names = owners(cfg)
    missing = names if refresh else [n for n in names if n not in have]
    if not missing:
        print(f'{len(have)} avatars already vendored, nothing to fetch')
        return

    added = 0
    for owner in missing:
        try:
            blob = fetch(owner)
        except (urllib.error.URLError, OSError) as exc:
            print(f'  {owner}: {exc}, skipping (the card draws an initial instead)')
            continue
        if len(blob) > LIMIT:
            print(f'  {owner}: over {LIMIT} bytes, skipping')
            continue
        kind = mime(blob)
        if not kind:
            print(f'  {owner}: not a PNG or JPEG, skipping')
            continue
        have[owner] = {'mime': kind, 'data': base64.b64encode(blob).decode()}
        added += 1
        print(f'  {owner}: {kind}, {len(blob)} bytes')

    # drop anyone no longer listed, so deleting a favourite cleans up after it
    have = {k: v for k, v in have.items() if k in names}
    AVATARS.write_text(json.dumps(have))
    print(f'{added} added, {len(have)} avatars in avatars.json')


if __name__ == '__main__':
    main(refresh='--refresh' in sys.argv)

#!/usr/bin/env python3
"""Vendor the devicon glyphs the profile needs into icons.json.

They have to be vendored. GitHub embeds these SVGs through <img>, which puts
them in the browser's secure static mode with external references switched
off, so an <image href="https://cdn..."> inside one of our SVGs silently
never loads. Same reason the Octicon path data is already in this file.

What gets fetched is whatever the config names: the languages in
[lines.devicon] plus every icon in [tools]. An icon already in icons.json is
left alone, and one devicon simply hasn't got - Databricks, Scheme, SQL - is
remembered as absent so it isn't chased again. With nothing left to look for
this doesn't touch the network at all, so the daily workflow run costs
nothing. `--refresh` re-fetches everything and reconsiders the absent ones,
which is how you pick up an icon devicon has added since.

devicon's icons come in variants. We prefer `plain`, then `original`, then
`line`: `plain` is the flat single-colour mark, which is what we want since
every glyph here is tinted by the code that draws it - Linguist's colour in
the language chart, the brand colour on a tool chip. Rust and C have no
`plain`, and fall back to `original`, which happens to be flat too.

Anything that isn't plain path data (gradients, groups, several different
fills) is refused rather than written out half-broken.

Usage:  python3 build_icons.py [--refresh]
"""
import json
import pathlib
import re
import sys
import urllib.error
import urllib.request

from build_data import EXT
from config import devicon_name, load

HERE = pathlib.Path(__file__).resolve().parent
ICONS = HERE / 'icons.json'
RAW = 'https://raw.githubusercontent.com/devicons/devicon/master'
MANIFEST = f'{RAW}/devicon.json'
PREFERRED = ('plain', 'original', 'line')
KIND = 'dev'
ABSENT = 'dev_absent'      # asked for once, devicon hasn't got it, don't ask again

VIEWBOX = re.compile(r'viewBox="([^"]+)"')
PATH_D = re.compile(r'<path\b[^>]*?\bd="([^"]+)"', re.S)
FILL = re.compile(r'fill="([^"]*)"')
DISALLOWED = re.compile(r'<(linearGradient|radialGradient|style|image|use|text)\b')


def fetch(url):
    with urllib.request.urlopen(url, timeout=30) as resp:
        return resp.read().decode()


def wanted(cfg):
    """Every icon name the profile could ask for: one per language the
    counter knows about (build_data.EXT), plus every tool chip."""
    out = {devicon_name(cfg, lang): 'language' for lang in sorted(set(EXT.values()))}
    for item in cfg['tools']['items']:
        if item.get('icon'):
            out[item['icon']] = 'tool'
    return out


def pick_variant(entry):
    available = entry.get('versions', {}).get('svg', [])
    for variant in PREFERRED:
        if variant in available:
            return variant
    return available[0] if available else None


def extract(svg, source):
    """Path data with the fills stripped, so the drawing code can tint it."""
    if DISALLOWED.search(svg):
        print(f'  {source}: not flat path data, skipping')
        return None
    paths = PATH_D.findall(svg)
    if not paths:
        print(f'  {source}: no <path> found, skipping')
        return None
    fills = {f for f in FILL.findall(svg) if f.lower() not in ('none', 'currentcolor')}
    if len(fills) > 1:
        print(f'  {source}: {len(fills)} different fills, skipping')
        return None
    box = VIEWBOX.search(svg)
    return {'vb': box.group(1) if box else '0 0 128 128', 'd': paths, 'src': source}


def main(refresh=False):
    icons = json.loads(ICONS.read_text())
    have = icons.get(KIND, {})
    absent = set() if refresh else set(icons.get(ABSENT, []))
    names = wanted(load())
    missing = sorted(n for n in names if refresh or (n not in have and n not in absent))
    if not missing:
        print(f'{len(have)} devicon glyphs vendored, {len(absent)} known absent, '
              f'nothing to fetch')
        return

    print(f'fetching {len(missing)} of {len(names)}: {", ".join(missing)}')
    manifest = {entry['name']: entry for entry in json.loads(fetch(MANIFEST))}

    added = 0
    for name in missing:
        entry = manifest.get(name)
        if not entry:
            absent.add(name)
            print(f'  {name}: not in devicon (it keeps its colour dot)')
            continue
        variant = pick_variant(entry)
        source = f'{name}-{variant}'
        try:
            svg = fetch(f'{RAW}/icons/{name}/{source}.svg')
        except urllib.error.URLError as exc:
            print(f'  {source}: {exc}, skipping')
            continue
        icon = extract(svg, source)
        if not icon:
            absent.add(name)
            continue
        # devicon's own brand colour, used when a tool chip is drawn; the
        # language chart ignores it and uses Linguist's instead
        if entry.get('color'):
            icon['color'] = entry['color']
        have[name] = icon
        added += 1
        print(f'  {name}: {source}, {len(icon["d"])} path(s), '
              f'{sum(len(d) for d in icon["d"])} chars')

    icons[KIND] = dict(sorted(have.items()))
    icons[ABSENT] = sorted(absent - set(have))
    ICONS.write_text(json.dumps(icons))
    print(f'{added} added, {len(have)} devicon glyphs in icons.json, '
          f'{len(icons[ABSENT])} known absent')


if __name__ == '__main__':
    main(refresh='--refresh' in sys.argv)

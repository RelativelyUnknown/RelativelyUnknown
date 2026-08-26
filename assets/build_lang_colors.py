#!/usr/bin/env python3
"""Rebuild lang-colors.json straight from GitHub Linguist's own source of
truth, languages.yml - not from a third-party mirror.

languages.yml is simple enough (a flat mapping of language name -> a small
set of 2-space-indented fields) that it doesn't need a YAML library: we
just read `color:` directly, and for a language with no colour of its own,
follow its `group:` chain up to whichever ancestor has one (that's how
Linguist itself attributes a language's colour when none is set, e.g.
"Alpine Abuild" has no colour but groups under "Shell", which does).

Usage:  python3 build_lang_colors.py
"""
import json
import pathlib
import re
import urllib.request

URL = 'https://raw.githubusercontent.com/github-linguist/linguist/main/lib/linguist/languages.yml'
HERE = pathlib.Path(__file__).resolve().parent

TOP_LEVEL = re.compile(r'^(\S.*):\s*$')
FIELD = re.compile(r'^  (\w+):\s*"?([^"]*)"?\s*$')


def parse(text):
    colour, group = {}, {}
    current = None
    for line in text.splitlines():
        if not line or line.startswith('#'):
            continue
        m = TOP_LEVEL.match(line)
        if m:
            current = m.group(1)
            continue
        if current is None or line.startswith('   '):
            continue
        m = FIELD.match(line)
        if not m:
            continue
        key, val = m.group(1), m.group(2)
        if key == 'color':
            colour[current] = val
        elif key == 'group':
            group[current] = val
    return colour, group


def resolve(name, colour, group, seen=None):
    if name in colour:
        return colour[name]
    seen = seen or set()
    parent = group.get(name)
    if not parent or parent in seen:
        return None
    return resolve(parent, colour, group, seen | {name})


def main():
    with urllib.request.urlopen(URL, timeout=20) as resp:
        text = resp.read().decode()
    colour, group = parse(text)
    resolved = {name: resolve(name, colour, group) for name in {**colour, **group}}
    resolved = {name: c for name, c in resolved.items() if c}
    (HERE / 'lang-colors.json').write_text(json.dumps(resolved, sort_keys=True))
    print(f'{len(resolved)} language colours ({len(colour)} direct, '
         f'{len(resolved) - len(colour)} inherited via group)')


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""Fetch the repos I have starred into stars.json, newest star first.

Uses $STARS_TOKEN (the PROFILE_UPDATE_KEY secret, read-only) when set; without
it, falls back to the public list at /users/<login>/starred. Private repos are
never written down - this file ends up in a public README.

A failed fetch leaves the existing stars.json alone.

Usage:  python3 discover_stars.py [login]
"""
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request

from config import load

HERE = pathlib.Path(__file__).resolve().parent
OUT = HERE / 'stars.json'
API = 'https://api.github.com'


def get(url, token):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-readme-bot'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=20) as r:
        return json.loads(r.read())


def main(login):
    cfg = load()
    want = cfg['favourites']['stars_max'] + len(cfg['favourites']['stars_exclude']) \
        + len(cfg['favourites']['items']) + 5
    token = os.environ.get('STARS_TOKEN')
    base = f'{API}/user/starred' if token else f'{API}/users/{login}/starred'
    stars, page = [], 1
    while len(stars) < want and page <= 5:
        try:
            batch = get(f'{base}?per_page=100&page={page}', token)
        except (urllib.error.URLError, OSError) as exc:
            print(f'could not fetch stars ({exc}); keeping the existing stars.json')
            return
        stars += [{'owner': r['owner']['login'], 'repo': r['name'],
                   'description': r.get('description') or ''}
                  for r in batch if not r.get('private')]
        if len(batch) < 100:
            break
        page += 1
    OUT.write_text(json.dumps({'stars': stars[:want]}, indent=2) + '\n')
    print(f'{len(stars[:want])} starred repos written to stars.json '
          f'({"authenticated" if token else "public list"})')


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else load()['profile']['login'])

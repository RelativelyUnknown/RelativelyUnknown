#!/usr/bin/env python3
"""First pass: find every repo I own, and every repo I've contributed to
without owning, then merge the result into repos.json.

repos.json is an append-only ledger. A repo already in it keeps its
`hue` and `first_seen` untouched forever - only a repo we've never seen
before gets a new one, chosen by hues.next_hue() to fill the biggest gap
left by every hue already handed out. That's what keeps a given repo's
colour in the Sankey stable release over release, instead of drifting as
commit counts (and therefore sort order) shift week to week.

Owned repos come from the REST API (no auth needed, works for public
repos, better rate limit with a token). Contributed-but-not-owned repos
come from the GraphQL contributionsCollection, which needs a token -
skipped with a warning if GITHUB_TOKEN isn't set.

Usage:  python3 discover_repos.py <login>        # defaults to $GITHUB_REPOSITORY_OWNER
"""
import datetime
import json
import os
import pathlib
import sys
import urllib.request

from hues import next_hue

HERE = pathlib.Path(__file__).resolve().parent
LEDGER = HERE / 'repos.json'
API = 'https://api.github.com'


def _request(url, token, method='GET', body=None):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-readme-bot'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    data = json.dumps(body).encode() if body is not None else None
    if data:
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read())


def owned_repos(login, token):
    out, page = [], 1
    while True:
        url = f'{API}/users/{login}/repos?type=owner&per_page=100&page={page}'
        batch = _request(url, token)
        if not batch:
            break
        out.extend((r['owner']['login'], r['name']) for r in batch)
        if len(batch) < 100:
            break
        page += 1
    return out


def contributed_repos(login, token):
    if not token:
        print('no GITHUB_TOKEN - skipping the contributed-repos pass (needs GraphQL auth)')
        return []
    query = '''
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          commitContributionsByRepository(maxRepositories: 100) {
            repository { nameWithOwner isPrivate }
          }
        }
      }
    }'''
    result = _request(f'{API}/graphql', token, method='POST',
                      body={'query': query, 'variables': {'login': login}})
    if 'errors' in result:
        print('GraphQL error, skipping contributed-repos pass:', result['errors'])
        return []
    rows = result['data']['user']['contributionsCollection']['commitContributionsByRepository']
    out = []
    for row in rows:
        if row['repository']['isPrivate']:
            continue
        owner, repo = row['repository']['nameWithOwner'].split('/', 1)
        if owner.lower() != login.lower():
            out.append((owner, repo))
    return out


def main(login):
    token = os.environ.get('GITHUB_TOKEN')
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {'repos': []}
    known = {(r['owner'], r['repo']): r for r in ledger['repos']}

    owned = owned_repos(login, token)
    contributed = [rc for rc in contributed_repos(login, token) if rc not in owned]

    today = datetime.date.today().isoformat()
    candidates = [(o, r, 'owner') for o, r in owned] + [(o, r, 'contributor') for o, r in contributed]
    new_count = 0
    for owner, repo, relation in candidates:
        key = (owner, repo)
        if key in known:
            continue
        hue = next_hue([r['hue'] for r in ledger['repos']])
        entry = {'owner': owner, 'repo': repo, 'relation': relation,
                 'hue': hue, 'first_seen': today}
        ledger['repos'].append(entry)
        known[key] = entry
        new_count += 1

    LEDGER.write_text(json.dumps(ledger, indent=2) + '\n')
    print(f'{login}: {len(owned)} owned, {len(contributed)} contributed (not owned), '
         f'{len(ledger["repos"])} tracked total, {new_count} new this run')


if __name__ == '__main__':
    login = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('GITHUB_REPOSITORY_OWNER')
    if not login:
        sys.exit('usage: discover_repos.py <login>  (or set GITHUB_REPOSITORY_OWNER)')
    main(login)

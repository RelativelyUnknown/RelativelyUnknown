#!/usr/bin/env python3
"""First pass: find every public repo I own, plus every public repo I've
committed to without owning, and merge the result into repos.json.

repos.json is a ledger, not a listing. A repo already in it keeps the
`swatch` and `first_seen` it was given the first time it showed up - only a
repo we've never seen before gets a new swatch, chosen by
palette.next_swatch() to be the least-used one so far. That's what keeps a
repo's colour in the Sankey stable release over release, instead of drifting
as commit counts (and therefore sort order) shift week to week.

Renames are followed by GitHub's numeric repo id rather than by name: the
entry keeps its swatch and its history, the old name moves into `aliases`,
and build_data.py stops cloning the repo twice under both names.

`description` is the repo's own GitHub description, refreshed on every run.
A repo with no description on GitHub keeps whatever text is already in the
ledger, so the cards have something to show.

`last_seen` is stamped on every repo the API still lists. Nothing is ever
deleted from the ledger - a repo you delete or make private keeps its colour
and its history here - but the stamp is how the generator tells which ones
are still public, so it stops counting the ones that aren't.

Owned repos come from the REST API (no auth needed for public repos, better
rate limit with a token). Contributed-but-not-owned repos come from the
GraphQL contributionsCollection, which needs a token - skipped with a
warning if GITHUB_TOKEN isn't set.

Usage:  python3 discover_repos.py <login>        # defaults to $GITHUB_REPOSITORY_OWNER
"""
import datetime
import json
import os
import pathlib
import sys
import urllib.request

from palette import next_swatch

HERE = pathlib.Path(__file__).resolve().parent
LEDGER = HERE / 'repos.json'
API = 'https://api.github.com'
FIELDS = ('owner', 'repo', 'id', 'relation', 'swatch', 'description',
          'first_seen', 'last_seen', 'aliases')


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
    """(id, owner, name, description) for every public repo `login` owns."""
    out, page = [], 1
    while True:
        url = f'{API}/users/{login}/repos?type=owner&per_page=100&page={page}'
        batch = _request(url, token)
        if not batch:
            break
        out.extend((r['id'], r['owner']['login'], r['name'], r['description'] or '')
                   for r in batch if not r['private'])
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
            repository { databaseId nameWithOwner description isPrivate }
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
        repo = row['repository']
        if repo['isPrivate']:
            continue
        owner, name = repo['nameWithOwner'].split('/', 1)
        if owner.lower() != login.lower():
            out.append((repo['databaseId'], owner, name, repo['description'] or ''))
    return out


def load_ledger():
    """Read repos.json, bringing entries written by older versions forward."""
    ledger = json.loads(LEDGER.read_text()) if LEDGER.exists() else {'repos': []}
    for entry in ledger['repos']:
        entry.pop('hue', None)  # the old HSL wheel; swatches replaced it
        entry.setdefault('description', '')
        if 'swatch' not in entry:
            entry['swatch'] = next_swatch([e.get('swatch') for e in ledger['repos']])
    return ledger


def order_fields(entry):
    known = {k: entry[k] for k in FIELDS if k in entry}
    known.update({k: v for k, v in entry.items() if k not in FIELDS})
    return known


def main(login):
    token = os.environ.get('GITHUB_TOKEN')
    ledger = load_ledger()
    by_id = {e['id']: e for e in ledger['repos'] if e.get('id')}
    by_name = {(e['owner'], e['repo']): e for e in ledger['repos']}

    owned = owned_repos(login, token)
    owned_names = {(o, n) for _, o, n, _ in owned}
    contributed = [r for r in contributed_repos(login, token) if (r[1], r[2]) not in owned_names]

    today = datetime.date.today().isoformat()
    seen = [(r, 'owner') for r in owned] + [(r, 'contributor') for r in contributed]
    new, renamed = 0, 0
    for (repo_id, owner, name, description), relation in seen:
        entry = by_id.get(repo_id) or by_name.get((owner, name))
        if entry is None:
            entry = {'owner': owner, 'repo': name, 'id': repo_id, 'relation': relation,
                     'swatch': next_swatch([e['swatch'] for e in ledger['repos']]),
                     'description': description,
                     'first_seen': today, 'last_seen': today}
            ledger['repos'].append(entry)
            by_id[repo_id] = entry
            by_name[(owner, name)] = entry
            new += 1
            continue
        if (entry['owner'], entry['repo']) != (owner, name):
            # renamed or transferred: same repo, keep its colour and its history
            entry.setdefault('aliases', []).append(entry['repo'])
            entry['owner'], entry['repo'] = owner, name
            by_name[(owner, name)] = entry
            renamed += 1
        entry['id'] = repo_id
        entry['relation'] = relation
        entry['last_seen'] = today
        if description:
            entry['description'] = description

    ledger['repos'] = [order_fields(e) for e in ledger['repos']]
    LEDGER.write_text(json.dumps(ledger, indent=2) + '\n')
    gone = [e['repo'] for e in ledger['repos'] if e.get('last_seen', today) != today]
    print(f'{login}: {len(owned)} owned, {len(contributed)} contributed (not owned), '
          f'{len(ledger["repos"])} tracked total, {new} new and {renamed} renamed this run')
    if gone:
        print(f'  no longer public (kept, not counted): {", ".join(sorted(gone))}')


if __name__ == '__main__':
    login = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('GITHUB_REPOSITORY_OWNER')
    if not login:
        sys.exit('usage: discover_repos.py <login>  (or set GITHUB_REPOSITORY_OWNER)')
    main(login)

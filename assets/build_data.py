#!/usr/bin/env python3
"""Recompute data.json from the local clones of the repositories.

Counts only commits authored by me — Claude, dependabot and (in forked or
contributed-to repos) other people's commits are excluded, so the stats and
the per-repo counts do not claim someone else's work.

Every count here (total, per-repo, and the language split used to weight
the Sankey) is windowed to the same last-52-weeks range, so they sum
consistently: total == sum(per_repo.values()).

The repo list itself lives in repos.json, not here - it's the ledger
discover_repos.py maintains (owned repos + repos I've contributed to
without owning), and it's also where each repo's Sankey hue is frozen
once assigned. See hues.py.

Usage:  python3 build_data.py ~/src        # dir holding the clones
"""
import collections
import datetime
import json
import os
import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
REPOS = [(r['owner'], r['repo']) for r in json.loads((HERE / 'repos.json').read_text())['repos']]

MINE = {'jurreandenys@gmail.com', '39960330+RedPandaMC@users.noreply.github.com'}
NOT_ME = ('claude', 'dependabot', 'bot]')

EXT = {'.py': 'Python', '.rs': 'Rust', '.ts': 'TypeScript', '.tsx': 'TypeScript',
       '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript', '.go': 'Go',
       '.c': 'C', '.h': 'C', '.scm': 'Scheme', '.sql': 'SQL', '.sh': 'Shell',
       '.vue': 'Vue'}
SKIP = {'.git', 'node_modules', 'target', 'dist', 'build', '.venv', 'venv',
        '__pycache__', 'out', 'coverage'}


def clone_dir(root, owner, repo):
    return root / f'{owner}__{repo}'


def commit_dates(path, since, until):
    """Dates of my commits in [since, until], one entry per commit."""
    log = subprocess.run(['git', '-C', str(path), 'log', f'--since={since}', f'--until={until}',
                          '--format=%ad\t%an\t%ae', '--date=short'],
                         capture_output=True, text=True).stdout
    out = []
    for line in log.strip().splitlines():
        date, name, email = line.split('\t')
        if email in MINE and not any(x in name.lower() for x in NOT_ME):
            out.append(date)
    return out


def language_split(path):
    sizes = collections.Counter()
    for dirpath, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for f in files:
            lang = EXT.get(os.path.splitext(f)[1])
            if lang:
                try:
                    sizes[lang] += os.path.getsize(os.path.join(dirpath, f))
                except OSError:
                    pass
    tot = sum(sizes.values()) or 1
    return [[l, round(v * 100 / tot, 1)] for l, v in sizes.most_common(4) if v * 100 / tot >= 1.0]


def main(root):
    root = pathlib.Path(root).expanduser()
    end = datetime.date.today()
    start = end - datetime.timedelta(weeks=52)

    days, per_repo, langs = collections.Counter(), collections.Counter(), {}
    for owner, repo in REPOS:
        path = clone_dir(root, owner, repo)
        if not path.exists():
            print(f'skip (not cloned): {owner}/{repo}')
            continue
        dates = commit_dates(path, start.isoformat(), end.isoformat())
        for d in dates:
            days[d] += 1
        if dates:
            per_repo[repo] += len(dates)
        split = language_split(path)
        if split:
            langs[repo] = split

    total = sum(days.values())
    out = {'total': total, 'active_days': len(days), 'peak': max(days.values(), default=0),
           'start': start.isoformat(), 'end': end.isoformat(),
           'per_repo': dict(per_repo), 'langs': langs}
    (HERE / 'data.json').write_text(json.dumps(out))
    print(f'{start} -> {end}: {total} commits on {out["active_days"]} days')
    print('per repo:', dict(per_repo))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')

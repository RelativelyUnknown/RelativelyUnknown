#!/usr/bin/env python3
"""Recompute data.json from the local clones of the repositories.

Counts only commits authored by me — Claude, dependabot and (in the forked
grammar) the upstream maintainers are excluded, so the heatmap and the
per-repo counts do not claim someone else's work.

Usage:  python3 build_data.py ~/src        # dir holding the clones
"""
import collections
import datetime
import json
import os
import pathlib
import subprocess
import sys

REPOS = ['Mallard', 'burnt', 'tree-sitter-sql-extended', 'RedPandaMC']
MINE = {'jurreandenys@gmail.com', '39960330+RedPandaMC@users.noreply.github.com'}
NOT_ME = ('claude', 'dependabot', 'bot]')

EXT = {'.py': 'Python', '.rs': 'Rust', '.ts': 'TypeScript', '.tsx': 'TypeScript',
       '.js': 'JavaScript', '.mjs': 'JavaScript', '.cjs': 'JavaScript', '.go': 'Go',
       '.c': 'C', '.h': 'C', '.scm': 'Scheme', '.sql': 'SQL', '.sh': 'Shell',
       '.vue': 'Vue'}
SKIP = {'.git', 'node_modules', 'target', 'dist', 'build', '.venv', 'venv',
        '__pycache__', 'out', 'coverage'}


def main(root):
    root = pathlib.Path(root).expanduser()
    days, per_repo = collections.Counter(), collections.Counter()
    for repo in REPOS:
        path = root / repo
        if not path.exists():
            print(f'skip (not cloned): {repo}')
            continue
        log = subprocess.run(['git', '-C', str(path), 'log', '--format=%ad\t%an\t%ae',
                              '--date=short'], capture_output=True, text=True).stdout
        for line in log.strip().splitlines():
            date, name, email = line.split('\t')
            if email in MINE and not any(x in name.lower() for x in NOT_ME):
                days[date] += 1
                per_repo[repo] += 1

    end = datetime.date.today()
    start = end - datetime.timedelta(weeks=52)
    counts = [c for date, c in days.items() if start.isoformat() <= date <= end.isoformat()]
    total = sum(counts)

    langs = {}
    for repo in REPOS[:3]:
        path = root / repo
        if not path.exists():
            continue
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
        langs[repo] = [(l, round(v * 100 / tot, 1))
                       for l, v in sizes.most_common(4) if v * 100 / tot >= 1.0]

    out = {'total': total, 'active_days': len(counts), 'peak': max(counts, default=0),
           'start': start.isoformat(), 'end': end.isoformat(),
           'per_repo': dict(per_repo), 'langs': langs}
    (pathlib.Path(__file__).resolve().parent / 'data.json').write_text(json.dumps(out))
    print(f'{start} -> {end}: {total} commits on {out["active_days"]} days')
    print('per repo:', dict(per_repo))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')

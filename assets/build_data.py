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
    end -= datetime.timedelta(days=(end.weekday() + 1) % 7)      # back to Sunday
    start = end - datetime.timedelta(weeks=51)
    grid = [[days.get((start + datetime.timedelta(weeks=w, days=d)).isoformat(), 0)
             for d in range(7)] for w in range(52)]
    total = sum(c for week in grid for c in week)

    months = []
    for w in range(52):
        d = start + datetime.timedelta(weeks=w)
        if d.day <= 7 and (not months or months[-1][1] != d.strftime('%b')):
            months.append((w, d.strftime('%b')))

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

    out = {'grid': grid, 'total': total,
           'active_days': sum(1 for week in grid for c in week if c),
           'peak': max((c for week in grid for c in week), default=0),
           'start': start.isoformat(), 'end': end.isoformat(), 'months': months,
           'per_repo': dict(per_repo), 'langs': langs}
    (pathlib.Path(__file__).resolve().parent / 'data.json').write_text(json.dumps(out))
    print(f'{start} -> {end}: {total} commits on {out["active_days"]} days')
    print('per repo:', dict(per_repo))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else '.')

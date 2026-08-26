#!/usr/bin/env python3
"""Print `owner repo` for every repo in repos.json, one per line.

Used by the daily GitHub Action to know what to clone for build_data.py.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent

if __name__ == '__main__':
    for r in json.loads((HERE / 'repos.json').read_text())['repos']:
        print(r['owner'], r['repo'])

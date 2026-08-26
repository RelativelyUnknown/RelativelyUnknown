#!/usr/bin/env python3
"""Print `owner repo` for every repo build_data.py reads, one per line.

Used by the daily GitHub Action to know what to clone, so the repo list
lives in exactly one place (build_data.py's REPOS).
"""
from build_data import REPOS

if __name__ == '__main__':
    for owner, repo in REPOS:
        print(owner, repo)

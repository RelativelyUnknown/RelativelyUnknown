#!/usr/bin/env python3
"""Stable, analogous hue assignment for repo colours in the commit-flow Sankey.

A repo's hue is assigned once, the first time discover_repos.py sees it, and
then lives forever in repos.json - regenerating the SVGs never reassigns it,
so a repo's colour doesn't drift as commit counts (and therefore sort order)
shift week to week. New repos get the hue that maximises the minimum
distance to every hue already handed out, so however many repos accumulate,
they stay as spread out as the range allows.

The range itself sits either side of GitHub's brand green (~132deg on the
HSL wheel) - "analogous", not a full rainbow.
"""

LO, HI = 58, 206  # degrees; GitHub's brand green sits at ~132, dead centre


def next_hue(existing):
    """The hue (degrees) that best fills the largest gap left by `existing`."""
    pts = sorted(existing)
    gaps, prev = [], LO
    for h in pts:
        gaps.append((h - prev, prev, h))
        prev = h
    gaps.append((HI - prev, prev, HI))
    gaps.sort(key=lambda g: -g[0])
    _, a, b = gaps[0]
    return round((a + b) / 2, 1)


def hsl_hex(h, s, l):
    c = (1 - abs(2 * l - 1)) * s
    x = c * (1 - abs((h / 60) % 2 - 1))
    m = l - c / 2
    r, g, b = [(c, x, 0), (x, c, 0), (0, c, x), (0, x, c), (x, 0, c), (c, 0, x)][int(h // 60) % 6]
    return '#{:02x}{:02x}{:02x}'.format(*(round((v + m) * 255) for v in (r, g, b)))


def repo_hex(hue, theme):
    """A stored hue -> a concrete colour for this theme."""
    s = 0.68 if theme == 'light' else 0.62
    l = 0.4 if theme == 'light' else 0.68
    return hsl_hex(hue, s, l)

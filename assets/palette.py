#!/usr/bin/env python3
"""Repo colours for the commit-flow Sankey.

A repo gets a swatch the first time discover_repos.py sees it and keeps it:
the choice is stored in repos.json, so a repo's colour doesn't move around
when commit counts (and with them the sort order) change week to week.

The swatches are Primer's own foreground tokens - the colours GitHub uses
for links, labels and states - light value first, dark second. They are
picked from a list rather than generated off a hue wheel, which is how the
old version kept landing on olive and mustard.
"""
import collections

# github/primer/primitives: fgColor.accent, .success, .done, .severe,
# .sponsors, .attention, .danger. Light theme first, dark second.
SWATCHES = {
    'blue': ('#0969da', '#4493f8'),
    'green': ('#1a7f37', '#3fb950'),
    'purple': ('#8250df', '#a371f7'),
    'orange': ('#bc4c00', '#db6d28'),
    'pink': ('#bf3989', '#db61a2'),
    'yellow': ('#9a6700', '#d29922'),
    'red': ('#cf222e', '#f85149'),
}
ORDER = list(SWATCHES)

# fgColor.muted, for anything folded together rather than named.
NEUTRAL = ('#656d76', '#8b949e')


def next_swatch(existing):
    """The least-used swatch, ties broken by ORDER so the result is stable."""
    used = collections.Counter(s for s in existing if s in SWATCHES)
    return min(ORDER, key=lambda name: (used[name], ORDER.index(name)))


def swatch_hex(name, theme):
    light, dark = SWATCHES.get(name, NEUTRAL)
    return light if theme == 'light' else dark

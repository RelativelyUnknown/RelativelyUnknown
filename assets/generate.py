#!/usr/bin/env python3
"""Generate the SVG blocks and the README for the RelativelyUnknown profile.

Four blocks - header, a row of repo cards, a commit-flow Sankey, footer -
each written twice, light and dark. README.md is written by the same run, so
the links, the alt text and the images can't drift apart.

Which repos get a card is decided by the data, not by a list kept here: the
three with the most commits of mine in the last 52 weeks. The profile
already has a Pinned row, so repeating it would waste the space. Card text
is the repo's own GitHub description, copied into repos.json by
discover_repos.py.

Colours are GitHub's. Primer neutrals for the chrome, Primer's link and
success tokens for the two accents, Primer's foreground tokens for repo
colours in the Sankey (palette.py), and Linguist's colours for anything
language-shaped, which is what GitHub uses on a repo's language bar.

Motion is CSS @keyframes inside each SVG file. GitHub strips <style> from
README HTML but keeps it inside an SVG loaded as an image. Everything is
guarded by prefers-reduced-motion.

Octicon path data is vendored in icons.json (MIT, see CREDITS.md).
Numbers come from data.json - rebuild it with build_data.py, never by hand.
"""
import collections
import json
import pathlib

from palette import swatch_hex, NEUTRAL

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
ICONS = json.loads((HERE / 'icons.json').read_text())
DATA = json.loads((HERE / 'data.json').read_text())
REPOS = json.loads((HERE / 'repos.json').read_text())['repos']

LOGIN = 'RelativelyUnknown'
CARDS = 3          # repo cards in the row
TRACK = 1000       # every block is laid out on the same unit width
WINDOW = 'past year'

# Primer's neutrals, plus its link blue and success green as the only two
# accents. Nothing here is a custom colour.
THEMES = {
    'light': dict(canvas='#ffffff', subtle='#f6f8fa', border='#d0d7de', fg='#1f2328',
                  muted='#59636e', accent='#1a7f37', link='#0969da'),
    'dark': dict(canvas='#0d1117', subtle='#161b22', border='#30363d', fg='#e6edf3',
                 muted='#9198a1', accent='#3fb950', link='#4493f8'),
}

# Linguist's own language colours, rebuilt from languages.yml by
# build_lang_colors.py. A repo's colour is not one of these - see palette.py.
LANG = json.loads((HERE / 'lang-colors.json').read_text())

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


# =====================================================================
# THE LEDGER, AND THE NUMBERS KEYED THROUGH IT
# =====================================================================
BY_NAME = {}
for _r in REPOS:
    BY_NAME[_r['repo']] = _r
for _r in REPOS:
    for _alias in _r.get('aliases', []):
        BY_NAME.setdefault(_alias, _r)


def canon(name):
    """A repo name as the ledger knows it today, following renames."""
    entry = BY_NAME.get(name)
    return entry['repo'] if entry else name


def commits_by_repo():
    per = collections.Counter()
    for name, count in DATA['per_repo'].items():
        per[canon(name)] += count
    return per


def langs_by_repo():
    """Language splits, with a renamed repo's old key folded into the new one."""
    out = {canon(n): s for n, s in DATA['langs'].items() if canon(n) != n}
    out.update({n: s for n, s in DATA['langs'].items() if canon(n) == n})
    return out


PER_REPO = commits_by_repo()
LANGS = langs_by_repo()


# =====================================================================
# TEXT
# =====================================================================
# Rough advance widths as a fraction of the font size, enough to wrap a
# description or to lay out a legend without running off the card.
_NARROW = {c: 0.30 for c in "il|!.,;:'`()[]{}/\\-"}
_NARROW.update({c: 0.37 for c in 'ftrjI'})
_NARROW.update({c: 0.85 for c in 'mw'})
_NARROW.update({c: 0.92 for c in 'MW%@'})
_NARROW[' '] = 0.27


def tw(s, size):
    """Approximate rendered width of `s`."""
    total = 0.0
    for c in s:
        if c in _NARROW:
            total += _NARROW[c]
        elif c.isdigit():
            total += 0.56
        elif c.isupper():
            total += 0.68
        else:
            total += 0.545
    return total * size


def wrap(text, size, width, lines):
    """Greedy wrap into at most `lines` lines, ellipsising anything left over."""
    words, out, cur = text.split(), [], ''
    for i, word in enumerate(words):
        trial = f'{cur} {word}'.strip()
        if cur and tw(trial, size) > width:
            if len(out) + 1 == lines:      # no room for another line: cut here
                return out + [ellipsise(' '.join([cur] + words[i:]), size, width)]
            out.append(cur)
            cur = word
        else:
            cur = trial
    return out + [ellipsise(cur, size, width)] if cur else out


def ellipsise(s, size, width):
    if tw(s, size) <= width:
        return s
    while s and tw(s + '...', size) > width:
        s = s[:-1]
    return s.rstrip(' ,.') + '...'


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')


def sentence(items, last='and'):
    if len(items) < 2:
        return ''.join(items)
    return f'{", ".join(items[:-1])} {last} {items[-1]}'


# =====================================================================
# SVG PRIMITIVES
# =====================================================================
def var(colour):
    return colour if colour.startswith('#') else f'var(--{colour})'


def txt(x, y, s, size=13, fill='fg', weight='400', anchor='start', family=SANS, cls='',
        halo=False):
    c = f' class="{cls}"' if cls else ''
    # a halo in the canvas colour keeps a label readable where it has to sit
    # on top of something, without a box around it
    h = ' stroke="var(--canvas)" stroke-width="3.5" paint-order="stroke"' if halo else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{var(fill)}" text-anchor="{anchor}"{h}{c}>'
            f'{esc(s)}</text>')


def rect(x, y, w, h, fill=None, stroke=None, rx=0, sw=1, cls='', op=None):
    f = 'none' if fill is None else var(fill)
    s = f' stroke="{var(stroke)}" stroke-width="{sw}"' if stroke else ''
    c = f' class="{cls}"' if cls else ''
    o = f' fill-opacity="{op}"' if op is not None else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{s}{c}{o}/>'


def icon(kind, name, x, y, size, colour):
    ic = ICONS[kind][name]
    vb = [float(v) for v in ic['vb'].split()]
    scale = size / vb[2]
    paths = ''.join(f'<path d="{d}"/>' for d in ic['d'])
    return (f'<g transform="translate({x},{y}) scale({scale:.5f})" '
            f'fill="{var(colour)}">{paths}</g>')


def card(w, h, rx=6):
    return rect(0.5, 0.5, round(w - 1, 2), round(h - 1, 2), 'canvas', 'border', rx=rx)


def style(theme):
    v = ';'.join(f'--{k}:{val}' for k, val in THEMES[theme].items())
    return ('<style>'
            f'svg{{{v}}}'
            # Every animated element rests VISIBLE: the motion is all in the
            # keyframes, with fill-mode both, so a block whose animation never
            # starts - browsers defer them for off-screen <img> SVGs - still
            # renders its content instead of nothing.
            '.rise{animation:rise .55s cubic-bezier(.2,.7,.2,1) both}'
            '@keyframes rise{from{opacity:0;transform:translateY(7px)}'
            'to{opacity:1;transform:none}}'
            '.bar{animation:grow 1s cubic-bezier(.2,.75,.2,1) both}'
            '@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
            '.pulse{animation:pulse 2.4s ease-in-out infinite}'
            '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.45}}'
            '@media (prefers-reduced-motion:reduce){'
            '.rise,.bar,.pulse{animation:none;opacity:1;transform:none}}'
            '</style>')


def svg(w, h, alt, theme, body, defs=''):
    d = f'<defs>{defs}</defs>' if defs else ''
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(alt)}">{style(theme)}{d}{body}</svg>\n')


def write(name, theme, content):
    d = ROOT / 'assets' if theme == 'light' else ROOT / 'assets' / 'dark'
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(content)


# =====================================================================
# HEADER
# =====================================================================
BIO = ['I write developer tooling for data platforms: parsers,',
       'linters, and a couple of VS Code extensions. Most of it',
       'started as something that annoyed me at work.']


def top_languages(n=3):
    weighted = collections.Counter()
    for repo, count in PER_REPO.items():
        for name, pct in LANGS.get(repo, []):
            weighted[name] += count * pct / 100
    return [name for name, _ in weighted.most_common(n)]


def header(theme):
    W, H = 1000, 224
    langs = top_languages()
    repo_count = sum(1 for r in REPOS if r.get('relation') == 'owner')
    facts = [('code-16', f'Mostly {sentence(langs)}'),
             ('repo-16', f'{repo_count} public repositories')]

    b = [card(W, H)]
    b.append(f'<g class="rise"><circle cx="32" cy="21" r="3.5" fill="var(--accent)"/>'
             f'{txt(42, 25, "Data and AI engineering", size=11.5, fill="muted")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.05s">'
             f'{txt(28, 62, LOGIN, size=28, weight="700")}</g>')
    b.append('<g class="rise" style="animation-delay:.1s">'
             + ''.join(txt(28, 92 + i * 22, line, size=14) for i, line in enumerate(BIO))
             + '</g>')
    for i, (glyph, label) in enumerate(facts):
        y = 172 + i * 24
        b.append(f'<g class="rise" style="animation-delay:{.2 + i * .06:.2f}s">'
                 f'{icon("oc", glyph, 28, y - 12, 14, "muted")}'
                 f'{txt(50, y, label, size=13, fill="muted")}</g>')

    stats = [(DATA['total'], f'commits, {WINDOW}'),
             (DATA['active_days'], 'days with commits'),
             (DATA['peak'], 'busiest day')]
    sx, sw = 592, 380
    for i, (n, label) in enumerate(stats):
        x = sx + i * (sw / 3)
        if i:
            b.append(f'<line x1="{x:.0f}" y1="80" x2="{x:.0f}" y2="180" stroke="var(--border)"/>')
        cx = x + sw / 6
        b.append(f'<g class="rise" style="animation-delay:{.28 + i * .08:.2f}s">'
                 f'{txt(cx, 128, str(n), size=30, weight="700", anchor="middle")}'
                 f'{txt(cx, 154, label, size=11.5, fill="muted", anchor="middle")}</g>')

    alt = (f'{LOGIN}, data and AI engineering. {" ".join(BIO)} Mostly {sentence(langs)}, across '
           f'{repo_count} public repositories. {DATA["total"]} commits in the {WINDOW} on '
           f'{DATA["active_days"]} days, {DATA["peak"]} of them on the busiest day.')
    return svg(W, H, alt, theme, ''.join(b)), alt


# =====================================================================
# REPO CARDS
# =====================================================================
def repo_card(theme, name, description, langs, commits, slot=0, of=CARDS):
    """One card, sized to a 1/`of` slice of the same 1000-unit track the
    full-width blocks use. The gutter between cards is transparent margin
    inside the slice, so the row lines up flush with the blocks above and
    below instead of sitting inset from them."""
    H, gutter = 190, 16
    slot_w = TRACK / of
    W = (TRACK - gutter * (of - 1)) / of
    dx = slot * (W + gutter - slot_w)
    inner = W - 40
    b = [card(W, H)]

    b.append(icon('oc', 'repo-16', 20, 26, 15, 'muted'))
    pill_x = round(W - 76, 2)
    b.append(txt(44, 38, ellipsise(name, 13, pill_x - 54), size=13, weight='600', fill='link'))
    b.append(rect(pill_x, 24, 58, 19, None, 'border', rx=9))
    b.append(txt(round(W - 47, 2), 37, 'Public', size=10.5, fill='muted', anchor='middle'))

    for i, line in enumerate(wrap(description, 11.5, inner, 2)):
        b.append(txt(20, 66 + i * 17, line, size=11.5, fill='muted'))

    total = sum(p for _, p in langs) or 1
    off = 0.0
    b.append('<g transform="translate(20,106)">')
    for i, (lname, pct) in enumerate(langs):
        seg = inner * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="8" rx="2" '
                 f'fill="{LANG.get(lname, NEUTRAL[0])}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0;animation-delay:{.25 + i * .08:.2f}s"/>')
        off += seg
    b.append('</g>')

    # the legend is laid out on measured widths, and stops at the card edge
    # rather than running off it
    lx, shown = 20.0, []
    for i, (lname, pct) in enumerate(langs):
        label = f'{lname} {pct:g}%'
        width = 12 + tw(label, 9.5)
        if lx + width > 20 + inner:
            break
        b.append(f'<g class="rise" style="animation-delay:{.4 + i * .06:.2f}s">'
                 f'<circle cx="{lx + 4:.1f}" cy="130" r="4" '
                 f'fill="{LANG.get(lname, NEUTRAL[0])}"/>'
                 f'{txt(round(lx + 12, 1), 134, label, size=9.5, fill="muted")}</g>')
        shown.append(label)
        lx += width + 14

    meta = f'{commits} commits, {WINDOW}'
    b.append(icon('oc', 'history-16', 20, 156, 12, 'muted'))
    b.append(txt(36, 166, meta, size=10.5, fill='muted'))

    alt = ' '.join(filter(None, [f'{name}.', description,
                                 ', '.join(shown) + '.' if shown else '', f'{meta}.']))
    body = f'<g transform="translate({dx:.3f},0)">{"".join(b)}</g>'
    return svg(round(slot_w, 2), H, alt, theme, body), alt


# =====================================================================
# COMMIT-FLOW SANKEY  (commits -> repo -> language)
# =====================================================================
def _apply_pct(total, pcts):
    """Largest-remainder rounding: whole numbers that still sum to `total`."""
    raw = [(name, total * pct / 100) for name, pct in pcts]
    floors = [(name, int(v), v - int(v)) for name, v in raw]
    used = sum(f for _, f, _ in floors)
    floors.sort(key=lambda t: -t[2])
    out = {name: f for name, f, _ in floors}
    for i in range(total - used):
        out[floors[i % len(floors)][0]] += 1
    return out


OTHER_REPOS, OTHER_LANGS = 'Other repos', 'Other languages'


def _fold(counts, floor, label):
    """Roll everything under `floor` into one bucket - but only if there is
    more than one of them, since folding a single repo just renames it."""
    small = [k for k, v in counts.items() if v < floor and k != label]
    if len(small) < 2:
        return dict(counts), set()
    kept = {k: v for k, v in counts.items() if k not in small}
    kept[label] = kept.get(label, 0) + sum(counts[k] for k in small)
    return kept, set(small)


def _sankey_data():
    per_repo = {r: c for r, c in PER_REPO.items() if c > 0}
    total = sum(per_repo.values())

    repos, folded_repos = _fold(per_repo, max(5, round(total * 0.01)), OTHER_REPOS)
    repo_order = sorted(repos, key=repos.get, reverse=True)

    # every repo's commits, split across the languages that repo is written in
    flows = collections.defaultdict(collections.Counter)
    for repo, count in per_repo.items():
        node = OTHER_REPOS if repo in folded_repos else repo
        split = LANGS.get(repo)
        flows[node].update(_apply_pct(count, split) if split else {OTHER_LANGS: count})

    lang_totals = collections.Counter()
    for repo_flows in flows.values():
        lang_totals.update(repo_flows)
    langs, folded_langs = _fold(lang_totals, max(8, round(total * 0.015)), OTHER_LANGS)
    lang_order = sorted(langs, key=langs.get, reverse=True)
    if OTHER_LANGS in lang_order:      # the catch-all always sorts last
        lang_order.append(lang_order.pop(lang_order.index(OTHER_LANGS)))

    links = [('commits', r, repos[r]) for r in repo_order]
    for repo in repo_order:
        merged = collections.Counter()
        for lang, v in flows[repo].items():
            merged[OTHER_LANGS if lang in folded_langs else lang] += v
        links += [(repo, lang, merged[lang]) for lang in lang_order if merged[lang]]

    columns = [[dict(id='commits', label='Commits', value=total)],
               [dict(id=r, label=r, value=repos[r]) for r in repo_order],
               [dict(id=l, label=l, value=langs[l]) for l in lang_order]]
    return columns, links


def _fit_scale(columns, inner_h, gap, min_slot):
    """Pixels per commit: as large as fits once every node is given room for
    its two-line label. One scale for all three columns, so the ribbons line
    up on both ends."""
    def used(scale):
        return max(sum(max(n['value'] * scale, min_slot) for n in col) + gap * (len(col) - 1)
                   for col in columns)
    lo, hi = 0.0, inner_h / max(n['value'] for col in columns for n in col)
    for _ in range(50):
        mid = (lo + hi) / 2
        if used(mid) <= inner_h:
            lo = mid
        else:
            hi = mid
    return lo


def sankey(theme):
    columns, links = _sankey_data()
    W, H, pad, node_w, gap = 1000, 460, 26, 16, 10
    # gutters either side for the first and last columns' labels, so they sit
    # beside their node instead of on top of the ribbons
    left, right = 96, 118
    inner_h = H - 2 * pad - 34
    min_slot = min(26, (inner_h - gap * (max(len(c) for c in columns) - 1))
                   / max(len(c) for c in columns))
    scale = _fit_scale(columns, inner_h, gap, min_slot)
    col_gap = (W - left - right - node_w * len(columns)) / (len(columns) - 1)

    colours = {'commits': THEMES[theme]['accent']}
    for entry in REPOS:
        colours[entry['repo']] = swatch_hex(entry['swatch'], theme)
    fallback = NEUTRAL[0] if theme == 'light' else NEUTRAL[1]
    for col in columns[2]:
        colours[col['id']] = LANG.get(col['id'], fallback)
    colours.setdefault(OTHER_REPOS, fallback)
    colours[OTHER_LANGS] = fallback

    pos = {}
    for ci, col in enumerate(columns):
        slots = [max(n['value'] * scale, min_slot) for n in col]
        y = pad + 34 + (inner_h - sum(slots) - gap * (len(col) - 1)) / 2
        for n, slot in zip(col, slots):
            h = max(n['value'] * scale, 2.5)
            top = y + (slot - h) / 2
            pos[n['id']] = dict(x=left + ci * (node_w + col_gap), y0=top, y1=top + h,
                                mid=y + slot / 2, col=ci, left=top, right=top, **n)
            y += slot + gap

    defs, b = [], [card(W, H)]
    ribbon_op = 0.4 if theme == 'light' else 0.5
    subtitle = f'{DATA["total"]} commits, {WINDOW}, by repo and then by language'
    b.append(f'<g class="rise">{txt(28, 32, "Commit flow", size=15, weight="600")}'
             f'{txt(W - 28, 32, subtitle, size=11.5, fill="muted", anchor="end")}</g>')

    for i, (src, tgt, value) in enumerate(links):
        s, t = pos[src], pos[tgt]
        h = value * scale
        sy, ty = s['right'], t['left']
        s['right'] += h
        t['left'] += h
        x0, x1 = s['x'] + node_w, t['x']
        xm = (x0 + x1) / 2
        d = (f'M{x0:.1f},{sy:.1f} C{xm:.1f},{sy:.1f} {xm:.1f},{ty:.1f} {x1:.1f},{ty:.1f} '
             f'L{x1:.1f},{ty + h:.1f} C{xm:.1f},{ty + h:.1f} {xm:.1f},{sy + h:.1f} '
             f'{x0:.1f},{sy + h:.1f} Z')
        # every ribbon fades from where it comes from to where it goes: green
        # into the repo's colour on the first hop, the repo's colour into the
        # language's on the second. A band stays followable across the
        # crossings instead of blending into mud
        defs.append(f'<linearGradient id="f{i}" gradientUnits="userSpaceOnUse" '
                    f'x1="{x0:.1f}" x2="{x1:.1f}">'
                    f'<stop offset="0" stop-color="{colours[src]}"/>'
                    f'<stop offset="1" stop-color="{colours[tgt]}"/></linearGradient>')
        b.append(f'<path d="{d}" fill="url(#f{i})" fill-opacity="{ribbon_op}" class="rise" '
                 f'style="animation-delay:{.15 + i * .02:.2f}s"/>')

    for col in columns:
        for n in col:
            p = pos[n['id']]
            delay = .05 if p['col'] == 0 else .15 + p['col'] * .1
            if p['col'] == 0:
                lx, anchor = p['x'] - 10, 'end'
            else:
                lx, anchor = p['x'] + node_w + 10, 'start'
            value = f'{n["value"]:g}'
            b.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                     f'<rect x="{p["x"]:.1f}" y="{p["y0"]:.1f}" width="{node_w}" '
                     f'height="{p["y1"] - p["y0"]:.1f}" rx="2" fill="{colours[n["id"]]}"/>'
                     f'{txt(lx, p["mid"] - 2, n["label"], size=11.5, weight="600", anchor=anchor, halo=True)}'
                     f'{txt(lx, p["mid"] + 12, value, size=10.5, fill="muted", anchor=anchor, family=MONO, halo=True)}'
                     '</g>')

    alt = (f'Commit flow: {DATA["total"]} commits in the {WINDOW}, from repo to language, sized '
           'by commits. ' + ', '.join(f'{n["label"]} {n["value"]:g}'
                                      for n in columns[1] + columns[2]) + '.')
    return svg(W, H, alt, theme, ''.join(b), defs=''.join(defs)), alt


# =====================================================================
# LINES BY LANGUAGE
# =====================================================================
def _line_rows(top=8):
    """(language, lines, share of every line counted), biggest first, with
    the tail rolled into one row."""
    counts = collections.Counter(DATA.get('lines') or {})
    total = sum(counts.values())
    if not total:
        return [], 0
    rows = counts.most_common(top)
    tail = total - sum(v for _, v in rows)
    if tail:
        rows.append((OTHER_LANGS, tail))
    return [(name, v, 100 * v / total) for name, v in rows], total


def lines_card(theme):
    rows, total = _line_rows()
    if not rows:
        return None, None
    W, row_h, top = TRACK, 30, 66
    H = top + row_h * len(rows) + 12
    x0, x1 = 196, 792                       # the bar's own track
    longest = max(v for _, v, _ in rows)
    fallback = NEUTRAL[0] if theme == 'light' else NEUTRAL[1]

    repos = DATA.get('line_repos') or sum(1 for r in REPOS if r.get('relation') == 'owner')
    subtitle = f'{total:,} lines across {repos} public repositories'
    b = [card(W, H)]
    b.append(f'<g class="rise">{txt(28, 32, "Lines by language", size=15, weight="600")}'
             f'{txt(W - 28, 32, subtitle, size=11.5, fill="muted", anchor="end")}</g>')

    for i, (name, count, pct) in enumerate(rows):
        y = top + i * row_h
        colour = fallback if name == OTHER_LANGS else LANG.get(name, fallback)
        width = max((x1 - x0) * count / longest, 3)
        b.append(f'<g class="rise" style="animation-delay:{.1 + i * .05:.2f}s">'
                 f'<circle cx="32" cy="{y - 4}" r="4" fill="{colour}"/>'
                 f'{txt(46, y, name, size=12)}'
                 f'{txt(x1 + 88, y, f"{count:,}", size=11.5, anchor="end", family=MONO)}'
                 f'{txt(W - 28, y, f"{pct:.1f}%", size=11.5, fill="muted", anchor="end")}'
                 f'</g>')
        b.append(f'<rect x="{x0}" y="{y - 8.5}" width="{width:.1f}" height="9" rx="2" '
                 f'fill="{colour}" class="bar" '
                 f'style="transform-origin:{x0}px 0;animation-delay:{.2 + i * .05:.2f}s"/>')

    alt = ('Lines by language across ' + str(repos) + f' public repositories, {total:,} in total: '
           + ', '.join(f'{n} {v:,} ({p:.1f}%)' for n, v, p in rows) + '.')
    return svg(W, H, alt, theme, ''.join(b)), alt


# =====================================================================
# FOOTER
# =====================================================================
FOOTER = 'Happy to talk about parsers, static analysis, or why your SQL is slow.'


def footer(theme):
    W, H = 1000, 76
    b = [card(W, H),
         '<circle cx="32" cy="41" r="5" fill="var(--accent)" class="pulse"/>',
         txt(50, 46, FOOTER, size=13.5)]
    return svg(W, H, FOOTER, theme, ''.join(b)), FOOTER


# =====================================================================
# README
# =====================================================================
def picture(name, alt, width='100%'):
    return (f'<picture><source media="(prefers-color-scheme: dark)" '
            f'srcset="assets/dark/{name}"/><img src="assets/{name}" alt="{esc(alt)}" '
            f'width="{width}"/></picture>')


def readme(alts, cards):
    """The whole file. The card row is emitted without a line break between
    the links: whitespace between them would count against the 100% the three
    cards add up to, and push the row out of line with the blocks around it."""
    row = ''.join(f'<a href="https://github.com/{entry["owner"]}/{entry["repo"]}">'
                  f'{picture(name, alt, width=f"{100 / CARDS:.2f}%")}</a>'
                  for entry, name, alt in cards)
    blocks = [picture('header.svg', alts['header.svg']),
              f'<p align="center">{row}</p>',
              picture('sankey.svg', alts['sankey.svg'])]
    if 'lines.svg' in alts:
        blocks.append(picture('lines.svg', alts['lines.svg']))
    blocks.append(picture('footer.svg', alts['footer.svg']))
    return '\n\n'.join(blocks) + '\n'


# =====================================================================
def active_repos(n=CARDS):
    """The repos with the most commits of mine in the window. The profile
    repo itself is left out - it is the page you are already looking at."""
    ranked = sorted(PER_REPO.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(BY_NAME[name], count) for name, count in ranked
            if name in BY_NAME and name != LOGIN][:n]


def slug(name):
    return 'repo-' + ''.join(c if c.isalnum() else '-' for c in name.lower()).strip('-') + '.svg'


if __name__ == '__main__':
    cards, alts = [], {}
    for slot, (entry, count) in enumerate(active_repos()):
        name = slug(entry['repo'])
        for theme in ('light', 'dark'):
            content, alt = repo_card(theme, entry['repo'], entry.get('description', ''),
                                     LANGS.get(entry['repo'], []), count, slot=slot)
            write(name, theme, content)
        cards.append((entry, name, alt))

    for theme in ('light', 'dark'):
        for block, name in ((header, 'header.svg'), (sankey, 'sankey.svg'),
                            (lines_card, 'lines.svg'), (footer, 'footer.svg')):
            content, alt = block(theme)
            if content is None:      # no line counts in data.json yet
                continue
            write(name, theme, content)
            alts[name] = alt

    keep = set(alts) | {name for _, name, _ in cards}
    for stale in sorted(set(HERE.glob('*.svg')) | set((HERE / 'dark').glob('*.svg'))):
        if stale.name not in keep:
            stale.unlink()
            print(f'removed stale {stale.relative_to(ROOT)}')

    (ROOT / 'README.md').write_text(readme(alts, cards))
    print(f'wrote README.md and {2 * len(keep)} svg files (light + dark): '
          + ', '.join(entry['repo'] for entry, _, _ in cards))

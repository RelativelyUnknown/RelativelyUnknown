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

from config import devicon_name, load
from palette import swatch_hex, NEUTRAL

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
ICONS = json.loads((HERE / 'icons.json').read_text())
_avatars = HERE / 'avatars.json'
AVATARS = json.loads(_avatars.read_text()) if _avatars.exists() else {}
DATA = json.loads((HERE / 'data.json').read_text())
REPOS = json.loads((HERE / 'repos.json').read_text())['repos']

# What the blocks say and how much they show is profile.toml's business; how
# they are drawn is this file's. See assets/config.py.
CFG = load()
LOGIN = CFG['profile']['login']
WINDOW = CFG['profile']['window']
CARDS = CFG['repos']['count']

TRACK = 1000       # every block is laid out on the same unit width
BIO_MEASURE = 380  # the header bio wraps to this, not to the space available

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
        # A refresh that ran while a rename was still two ledger entries has
        # the same repo in here twice, under both names. That is one repo's
        # commits described twice, not twice as many of them, so the bigger
        # count wins rather than the two being added up.
        per[canon(name)] = max(per[canon(name)], count)
    return per


def langs_by_repo():
    """Language splits, with a renamed repo's old key folded into the new one."""
    out = {canon(n): s for n, s in DATA['langs'].items() if canon(n) != n}
    out.update({n: s for n, s in DATA['langs'].items() if canon(n) == n})
    return out


PER_REPO = commits_by_repo()
LANGS = langs_by_repo()
# build_data.py writes total == sum(per_repo.values()), so recomputing it from
# the folded counts is the same number in a healthy data.json - and the honest
# one in a data.json that counted a renamed repo under both its names.
TOTAL = sum(PER_REPO.values()) or DATA['total']


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


def plural(n, thing, many=None):
    """"1 commit", "703 commits". Every number on this page is measured, so
    any of them can legitimately come out as one."""
    return f'{n:,} {thing if abs(n) == 1 else many or thing + "s"}'


def sentence(items, last='and'):
    if len(items) < 2:
        return ''.join(items)
    return f'{", ".join(items[:-1])} {last} {items[-1]}'


# =====================================================================
# SVG PRIMITIVES
# =====================================================================
def var(colour):
    return colour if colour.startswith('#') else f'var(--{colour})'


def txt(x, y, s, size=13, fill='fg', weight='400', anchor='start', family=SANS, cls=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{var(fill)}" text-anchor="{anchor}"{c}>{esc(s)}</text>')


def name_value(x, y, name, value, anchor='start', size=11.5, vsize=10.5, fill='fg'):
    """"burnt 207" as one text run: the name, then the count a fixed gap
    later. Two tspans rather than two <text>s, so the gap is the renderer's
    measurement of the name and not this file's guess at it."""
    return (f'<text x="{x}" y="{y}" font-family="{SANS}" font-size="{size}" '
            f'text-anchor="{anchor}" fill="{var(fill)}">'
            f'<tspan font-weight="600">{esc(name)}</tspan>'
            f'<tspan dx="7" font-family="{MONO}" font-size="{vsize}" fill="var(--muted)">'
            f'{esc(value)}</tspan></text>')


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


def lang_glyph(language):
    """The devicon glyph for a language, or None to fall back to its dot -
    Scheme and SQL have no icon anywhere, and that is fine."""
    if not CFG['lines']['icons']:
        return None
    name = devicon_name(CFG, language)
    return ('dev', name) if name in ICONS.get('dev', {}) else None


def tool_glyph(name):
    """devicon first, then the Simple Icons already vendored here, which
    still carry marks devicon has no icon for at all - Databricks, say."""
    for kind in ('dev', 'si'):
        if name in ICONS.get(kind, {}):
            return kind, name
    return None


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
def bio_lines():
    """The bio as drawn: a paragraph wrapped to the header's measure, or the
    lines exactly as given if the config supplies a list instead."""
    bio = CFG['header']['bio']
    if isinstance(bio, list):
        return bio
    return wrap(bio, 14, BIO_MEASURE, 4) if bio else []


def public_repos():
    """How many repos are still public. The ledger keeps a repo after it is
    deleted or made private - that is the point of a ledger, it holds the
    colour and the history - so counting every owned row would count those
    forever. discover_repos.py stamps last_seen on whatever the API still
    lists, and only the newest run's stamp counts. A ledger written before
    the stamp existed falls back to counting them all."""
    owned = [r for r in REPOS if r.get('relation') == 'owner']
    latest = max((r.get('last_seen', '') for r in owned), default='')
    if not latest:
        return len(owned)
    return sum(1 for r in owned if r.get('last_seen') == latest)


def top_languages(n=3):
    weighted = collections.Counter()
    for repo, count in PER_REPO.items():
        for name, pct in LANGS.get(repo, []):
            weighted[name] += count * pct / 100
    return [name for name, _ in weighted.most_common(n)]


def header(theme):
    W, H = 1000, 224
    langs = top_languages()
    repo_count = public_repos()
    facts = [('code-16', f'Mostly {sentence(langs)}'),
             ('repo-16', plural(repo_count, 'public repository', 'public repositories'))]

    b = [card(W, H)]
    b.append(f'<g class="rise"><circle cx="32" cy="21" r="3.5" fill="var(--accent)"/>'
             f'{txt(42, 25, CFG["header"]["eyebrow"], size=11.5, fill="muted")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.05s">'
             f'{txt(28, 62, LOGIN, size=28, weight="700")}</g>')
    bio = bio_lines()
    b.append('<g class="rise" style="animation-delay:.1s">'
             + ''.join(txt(28, 92 + i * 22, line, size=14) for i, line in enumerate(bio))
             + '</g>')
    for i, (glyph, label) in enumerate(facts):
        y = 172 + i * 24
        b.append(f'<g class="rise" style="animation-delay:{.2 + i * .06:.2f}s">'
                 f'{icon("oc", glyph, 28, y - 12, 14, "muted")}'
                 f'{txt(50, y, label, size=13, fill="muted")}</g>')

    stats = [(TOTAL, f'commits, {WINDOW}'),
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

    eyebrow = CFG['header']['eyebrow']
    alt = (f'{LOGIN}, {eyebrow[:1].lower() + eyebrow[1:]}. {" ".join(bio)} '
           f'Mostly {sentence(langs)}, across '
           f'{plural(repo_count, "public repository", "public repositories")}. '
           f'{plural(TOTAL, "commit")} in the {WINDOW} on '
           f'{plural(DATA["active_days"], "day")}, {DATA["peak"]} of them on the busiest day.')
    return svg(W, H, alt, theme, ''.join(b)), alt


# =====================================================================
# REPO CARDS
# =====================================================================
GUTTER = 16        # between cards in a row


def slot_geometry(slot, of):
    """A card that is one of `of` across the same 1000-unit track the
    full-width blocks use: its drawn width, the transparent margin inside its
    slice of the track, and the slice itself. Keeping the gutter as margin
    rather than as a gap between images is what makes a row line up flush with
    the blocks above and below instead of sitting inset from them."""
    slot_w = TRACK / of
    w = (TRACK - GUTTER * (of - 1)) / of
    return w, slot * (w + GUTTER - slot_w), slot_w


def repo_card(theme, name, description, langs, commits, slot=0, of=CARDS):
    H = 190
    W, dx, slot_w = slot_geometry(slot, of)
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

    meta = f'{plural(commits, "commit")}, {WINDOW}'
    b.append(icon('oc', 'history-16', 20, 156, 12, 'muted'))
    b.append(txt(36, 166, meta, size=10.5, fill='muted'))

    alt = ' '.join(filter(None, [f'{name}.', description,
                                 ', '.join(shown) + '.' if shown else '', f'{meta}.']))
    return svg(round(slot_w, 2), H, alt, theme,
               f'<g transform="translate({dx:.3f},0)">{"".join(b)}</g>'), alt


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

    floor = max(5, round(total * CFG['sankey']['fold_repos_pct'] / 100))
    repos, folded_repos = _fold(per_repo, floor, OTHER_REPOS)
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
    lang_floor = max(8, round(total * CFG['sankey']['fold_langs_pct'] / 100))
    langs, folded_langs = _fold(lang_totals, lang_floor, OTHER_LANGS)
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
    W, H = TRACK, CFG['sankey']['height']
    pad, node_w, gap = 26, 16, 10
    # gutters either side, wide enough for a one-line "name 123" label
    left, right = 120, 150
    inner_h = H - 2 * pad - 34
    # one line of label per node now, so a node needs less room to be legible
    # and more of the height goes to the flow itself
    min_slot = min(20, (inner_h - gap * (max(len(c) for c in columns) - 1))
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
    subtitle = f'{plural(TOTAL, "commit")}, {WINDOW}, by repo and then by language'
    b.append(f'<g class="rise">{txt(28, 32, CFG["sankey"]["title"], size=15, weight="600")}'
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

    # Labels: name and count on one line, set beside the node rather than
    # stacked on it. The outer two columns have the gutters to themselves. The
    # repo column reads to the LEFT of its node, where the only thing behind
    # the text is that repo's own incoming band - one flat colour with clean
    # gaps either side of it - instead of the fan-out on the right where the
    # ribbons cross each other. Nothing needs an outline to sit on.
    for col in columns:
        for n in col:
            p = pos[n['id']]
            delay = .05 if p['col'] == 0 else .15 + p['col'] * .1
            value = f'{n["value"]:g}'
            if p['col'] == len(columns) - 1:
                label = name_value(p['x'] + node_w + 12, p['mid'] + 4, n['label'], value)
            else:
                label = name_value(p['x'] - 12, p['mid'] + 4, n['label'], value,
                                   anchor='end')
            b.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">'
                     f'<rect x="{p["x"]:.1f}" y="{p["y0"]:.1f}" width="{node_w}" '
                     f'height="{p["y1"] - p["y0"]:.1f}" rx="2" fill="{colours[n["id"]]}"/>'
                     f'{label}</g>')

    alt = (f'Commit flow: {plural(TOTAL, "commit")} in the {WINDOW}, from repo to language, sized '
           'by commits. ' + ', '.join(f'{n["label"]} {n["value"]:g}'
                                      for n in columns[1] + columns[2]) + '.')
    return svg(W, H, alt, theme, ''.join(b), defs=''.join(defs)), alt


# =====================================================================
# LINES BY LANGUAGE
# =====================================================================
def _line_rows(top=None):
    """(language, lines, share of every line counted), biggest first, with
    the tail rolled into one row."""
    counts = collections.Counter(DATA.get('lines') or {})
    total = sum(counts.values())
    if not total:
        return [], 0
    rows = counts.most_common(top or CFG['lines']['top'])
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

    repos = DATA.get('line_repos') or public_repos()
    subtitle = (f'{plural(total, "line")} across '
                + plural(repos, 'public repository', 'public repositories'))
    b = [card(W, H)]
    b.append(f'<g class="rise">{txt(28, 32, CFG["lines"]["title"], size=15, weight="600")}'
             f'{txt(W - 28, 32, subtitle, size=11.5, fill="muted", anchor="end")}</g>')

    for i, (name, count, pct) in enumerate(rows):
        y = top + i * row_h
        colour = fallback if name == OTHER_LANGS else LANG.get(name, fallback)
        width = max((x1 - x0) * count / longest, 3)
        glyph = lang_glyph(name)
        # tinted with Linguist's colour, not devicon's, so the glyph, the bar
        # and the dots elsewhere on the page stay one colour system
        mark = (icon(glyph[0], glyph[1], 25, y - 11, 14, colour) if glyph
                else f'<circle cx="32" cy="{y - 4}" r="4" fill="{colour}"/>')
        b.append(f'<g class="rise" style="animation-delay:{.1 + i * .05:.2f}s">'
                 f'{mark}'
                 f'{txt(46, y, name, size=12)}'
                 f'{txt(x1 + 88, y, f"{count:,}", size=11.5, anchor="end", family=MONO)}'
                 f'{txt(W - 28, y, f"{pct:.1f}%", size=11.5, fill="muted", anchor="end")}'
                 f'</g>')
        b.append(f'<rect x="{x0}" y="{y - 8.5}" width="{width:.1f}" height="9" rx="2" '
                 f'fill="{colour}" class="bar" '
                 f'style="transform-origin:{x0}px 0;animation-delay:{.2 + i * .05:.2f}s"/>')

    alt = ('Lines by language across '
           + plural(repos, 'public repository', 'public repositories')
           + f', {plural(total, "line")} in total: '
           + ', '.join(f'{n} {v:,} ({p:.1f}%)' for n, v, p in rows) + '.')
    return svg(W, H, alt, theme, ''.join(b)), alt


# =====================================================================
# TOOLS
# =====================================================================
def _luminance(hex_colour):
    h = hex_colour.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def brand(colour, theme):
    """A tool's own brand colour, unless it would sink into this theme's
    canvas - Rust's black and Bash's near-black vanish on the dark one, and
    JavaScript's yellow does the same on the light one."""
    if not colour:
        return 'muted'
    light = _luminance(colour)
    if (theme == 'dark' and light < 0.25) or (theme == 'light' and light > 0.8):
        return 'muted'
    return colour


def tools_card(theme):
    items = CFG['tools']['items']
    if not items:
        return None, None
    W, top, chip_h, gap = TRACK, 56, 32, 10

    rows, x = [[]], 28
    for item in items:
        label = item.get('label') or item.get('icon', '')
        width = 12 + 16 + 8 + tw(label, 12) + 14
        if rows[-1] and x + width > W - 28:
            rows.append([])
            x = 28
        rows[-1].append((item, label, width))
        x += width + gap
    H = top + len(rows) * (chip_h + gap) - gap + 18

    b = [card(W, H)]
    if CFG['tools']['title']:
        b.append(f'<g class="rise">{txt(28, 32, CFG["tools"]["title"], size=15, weight="600")}</g>')

    labels, i = [], 0
    for r, row in enumerate(rows):
        x, y = 28, top + r * (chip_h + gap)
        for item, label, width in row:
            glyph = tool_glyph(item.get('icon', ''))
            # devicon ships a brand colour with each icon; the Simple Icons
            # fallback set doesn't, so an item can name its own
            known = ICONS[glyph[0]][glyph[1]].get('color') if glyph else None
            colour = brand(item.get('color') or known, theme)
            b.append(f'<g class="rise" style="animation-delay:{.1 + i * .04:.2f}s">'
                     f'{rect(round(x, 1), y, round(width, 1), chip_h, "canvas", "border", rx=16)}'
                     + (icon(glyph[0], glyph[1], round(x + 12, 1), y + 8, 16, colour) if glyph else '')
                     + f'{txt(round(x + (36 if glyph else 14), 1), y + 21, label, size=12)}</g>')
            labels.append(label)
            x += width + gap
            i += 1

    alt = f'{CFG["tools"]["title"] or "Tools"}: ' + sentence(labels) + '.'
    return svg(W, H, alt, theme, ''.join(b)), alt


# =====================================================================
# FAVOURITE PROJECTS
# =====================================================================
def url_parts(url):
    """('pydantic', 'pydantic') out of https://github.com/pydantic/pydantic."""
    tail = url.split('github.com/', 1)[-1].strip('/')
    bits = [b for b in tail.split('/') if b]
    return (bits + [None, None])[:2]


def avatar(owner, x, y, size):
    """The owner's picture, vendored as a data: URI by build_avatars.py. It
    has to be embedded - an SVG that GitHub serves through <img> cannot
    fetch anything. Until it has been fetched, or if it never can be, the
    card draws their initial instead of breaking."""
    r = size / 2
    cx, cy = x + r, y + r
    picture = AVATARS.get(owner)
    if picture:
        clip = 'av-' + ''.join(c for c in owner.lower() if c.isalnum())
        return (f'<clipPath id="{clip}"><circle cx="{cx}" cy="{cy}" r="{r}"/></clipPath>'
                f'<image href="data:{picture["mime"]};base64,{picture["data"]}" '
                f'x="{x}" y="{y}" width="{size}" height="{size}" '
                f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{clip})"/>')
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="var(--subtle)" '
            f'stroke="var(--border)"/>'
            + txt(cx, cy + 6, owner[:1].upper(), size=16, weight='600',
                  fill='muted', anchor='middle'))


def favourite_card(theme, item, slot=0, of=1):
    H = 96
    W, dx, slot_w = slot_geometry(slot, of)
    owner, repo = url_parts(item.get('url', ''))
    owner = item.get('owner') or owner or '?'
    name = item.get('name') or repo or owner

    b = [card(W, H), avatar(owner, 20, 30, 36)]
    # pydantic/pydantic reads as "pydantic pydantic" otherwise
    b.append(name_value(68, 44, name, '' if owner == name else owner, size=13, fill='link')
             if owner != name else txt(68, 44, name, size=13, weight='600', fill='link'))
    for i, line in enumerate(wrap(item.get('note', ''), 11.5, W - 88, 2)):
        b.append(txt(68, 64 + i * 16, line, size=11.5, fill='muted'))

    label = name if owner == name else f'{owner}/{name}'
    alt = ' '.join(filter(None, [f'{label}.', item.get('note', '')]))
    return svg(round(slot_w, 2), H, alt, theme,
               f'<g transform="translate({dx:.3f},0)">{"".join(b)}</g>'), alt


# =====================================================================
# FOOTER
# =====================================================================
def footer(theme):
    text = CFG['footer']['text']
    if not text:
        return None, None
    W, H = TRACK, 76
    b = [card(W, H),
         '<circle cx="32" cy="41" r="5" fill="var(--accent)" class="pulse"/>',
         txt(50, 46, text, size=13.5)]
    return svg(W, H, text, theme, ''.join(b)), text


# =====================================================================
# ROW HEADING
# =====================================================================
def heading(theme, title, subtitle=""):
    """A title for a block that is a row of separate linked images rather
    than one card, so it has nowhere to draw its own. Same x, size and
    weight as the titles inside the cards, so it lines up with them."""
    W, H = TRACK, 34
    b = [txt(28, 24, title, size=15, weight='600')]
    if subtitle:
        b.append(txt(W - 28, 24, subtitle, size=11.5, fill='muted', anchor='end'))
    alt = f'{title}. {subtitle}'.strip().rstrip('.') + '.'
    return svg(W, H, alt, theme, f'<g class="rise">{"".join(b)}</g>'), alt


# =====================================================================
# README
# =====================================================================
def picture(name, alt, width='100%'):
    return (f'<picture><source media="(prefers-color-scheme: dark)" '
            f'srcset="assets/dark/{name}"/><img src="assets/{name}" alt="{esc(alt)}" '
            f'width="{width}"/></picture>')


def readme(pieces, alts):
    """The whole file.

    Nothing inside a row is separated by whitespace: a space between the
    images counts against the 100% the cards add up to and pushes the row out
    of line with the full-width blocks around it. A row's heading sits in the
    same paragraph as its cards for the mirror-image reason - it is full
    width, so the cards wrap under it by themselves, and keeping them in one
    paragraph stops the paragraph margin floating the heading away from the
    row it belongs to.
    """
    blocks = []
    for kind, value in pieces:
        if kind == 'single':
            blocks.append(picture(value, alts[value]))
            continue
        head, cards = value
        width = f'{100 / len(cards):.2f}%'
        row = ''.join(f'<a href="{esc(url)}">{picture(name, alts[name], width)}</a>'
                      for name, url in cards)
        lead = picture(head, alts[head]) if head else ''
        blocks.append(f'<p align="center">{lead}{row}</p>')
    return '\n\n'.join(blocks) + '\n'


# =====================================================================
# THE BLOCKS THEMSELVES
# =====================================================================
def active_repos(n=None):
    """The repos with the most commits of mine in the window, minus anything
    repos.exclude names - the profile repo by default, since it is the page
    you are already looking at."""
    skip = set(CFG['repos']['exclude'])
    ranked = sorted(PER_REPO.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(BY_NAME[name], count) for name, count in ranked
            if name in BY_NAME and name not in skip][:n or CARDS]


def slug(prefix, name):
    return prefix + ''.join(c if c.isalnum() else '-' for c in name.lower()).strip('-') + '.svg'


def repo_row():
    """One row of cards for the most active repos: [[(file, url, draw)]]."""
    row = []
    for entry, count in active_repos():
        url = f'https://github.com/{entry["owner"]}/{entry["repo"]}'

        def draw(theme, slot, of, e=entry, c=count):
            return repo_card(theme, e['repo'], e.get('description', ''),
                             LANGS.get(e['repo'], []), c, slot=slot, of=of)

        row.append((slug('repo-', entry['repo']), url, draw))
    return [row] if row else []


# A block is either one full-width image, or a row of images that are links.
def favourite_row(per_row=3):
    """Linked cards for [[favourites.items]], at most `per_row` across."""
    items = CFG['favourites']['items']
    rows = []
    for start in range(0, len(items), per_row):
        chunk = items[start:start + per_row]
        row = []
        for item in chunk:
            owner, repo = url_parts(item.get('url', ''))
            key = f'{item.get("owner") or owner or "fav"}-{item.get("name") or repo or ""}'

            def draw(theme, slot, of, it=item):
                return favourite_card(theme, it, slot=slot, of=of)

            row.append((slug('fav-', key), item.get('url', ''), draw))
        rows.append(row)
    return rows


# Every block, in the order they belong in when nothing says otherwise. A
# block is either one full-width image, or a row of images that are links.
SINGLE_BLOCKS = {'header': header, 'sankey': sankey, 'lines': lines_card,
                 'tools': tools_card, 'footer': footer}
ROW_BLOCKS = {'repos': repo_row, 'favourites': favourite_row}
CANONICAL = ['header', 'repos', 'sankey', 'lines', 'tools', 'favourites', 'footer']

# what the heading above a row says on the right, where it is worth saying
SUBTITLES = {'repos': lambda: f'most commits of mine, {WINDOW}'}


def enabled(name):
    return bool(CFG.get(name, {}).get('enabled', True))


def block_order():
    """blocks.order decides the sequence, not the guest list. Anything that
    is switched on and has something to show gets added even when the order
    forgets it, so filling in a section is all it takes to put it on the
    page."""
    wanted = [name for name in CFG['blocks']['order'] if name in CANONICAL]
    for name in CFG['blocks']['order']:
        if name not in CANONICAL:
            print(f'profile.toml: blocks.order names "{name}", which is not a block')
    extra = [name for name in CANONICAL if name not in wanted and enabled(name)]
    if extra:
        print(f'blocks.order does not mention {", ".join(extra)}; '
              f'adding {"them" if len(extra) > 1 else "it"} in the usual place')
    return sorted(wanted + extra, key=CANONICAL.index)


def build():
    pieces, alts = [], {}
    for name in block_order():
        if not enabled(name):
            continue
        drew = False

        if name in ROW_BLOCKS:
            for cards in ROW_BLOCKS[name]():
                head = ''
                title = CFG[name].get('title', '')
                if title:
                    head = f'heading-{name}.svg'
                    subtitle = SUBTITLES.get(name, str)()
                    for theme in THEMES:
                        content, alt = heading(theme, title, subtitle)
                        write(head, theme, content)
                        alts[head] = alt
                for slot, (filename, url, draw) in enumerate(cards):
                    for theme in THEMES:
                        content, alt = draw(theme, slot, len(cards))
                        write(filename, theme, content)
                        alts[filename] = alt
                pieces.append(('row', (head, [(f, u) for f, u, _ in cards])))
                drew = True
        else:
            filename = f'{name}.svg'
            for theme in THEMES:
                content, alt = SINGLE_BLOCKS[name](theme)
                if content is None:      # nothing to draw - no data, or no text
                    break
                write(filename, theme, content)
                alts[filename] = alt
            else:
                pieces.append(('single', filename))
                drew = True

        if not drew:
            print(f'{name} is on but has nothing to show yet, so it is not in the README')
    return pieces, alts


if __name__ == '__main__':
    pieces, alts = build()

    for stale in sorted(set(HERE.glob('*.svg')) | set((HERE / 'dark').glob('*.svg'))):
        if stale.name not in alts:
            stale.unlink()
            print(f'removed stale {stale.relative_to(ROOT)}')

    (ROOT / 'README.md').write_text(readme(pieces, alts))
    print(f'wrote README.md and {2 * len(alts)} svg files (light + dark): '
          + ', '.join(sorted(alts)))

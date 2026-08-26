#!/usr/bin/env python3
"""Generate the SVG blocks for the RelativelyUnknown profile README.

Plain GitHub, one brand colour.

  Structure and colour are both Primer now: bordered cards at Primer's own
  radius, the real neutral tokens (#d0d7de / #30363d borders, not a custom
  palette), plain Octicons, a repo pin's actual "Public" pill. No dithering,
  no terminal prompts, no dark module screens - those were fun but they
  weren't GitHub.

  The one colour anywhere is GitHub's own brand green (from
  brand.github.com's published palette), used the way GitHub itself uses
  it: sparingly, as a status dot and a couple of small icons, never as a
  wash. Every language colour you see is Linguist's, because that's
  GitHub's own convention for a repo's language bar, not a decorative
  choice.

  The languages block is gone. In its place: a Sankey built from the same
  measured data - commits, per repo, into that repo's language split -
  hand-laid-out as one more generated SVG, no charting library. It only
  works because build_data.py windows every count (total, per-repo,
  language weighting) to the same last-52-weeks range, so the numbers
  actually conserve: total == sum of the repo nodes == sum of the
  language nodes.

Every block is emitted light and dark; the README picks with <picture>
media="(prefers-color-scheme: dark)", the only image theming GitHub honours.

Motion is CSS @keyframes inside each SVG file. GitHub strips <style> from
README HTML but keeps it inside an SVG loaded as an image. Everything is
guarded by prefers-reduced-motion.

Third-party artwork, vendored as path data in icons.json:
  Primer Octicons - MIT       https://github.com/primer/octicons

Numbers in data.json are measured, never asserted; rebuild with build_data.py.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ICONS = json.loads((HERE / 'icons.json').read_text())
DATA = json.loads((HERE / 'data.json').read_text())

# GitHub's own brand green (brand.github.com), light theme's hero step and a
# brighter step from the same ramp for legibility on a dark canvas.
GREEN = '#0FBF3E'
GREEN_DARK = '#5FED83'

# GitHub's real Primer neutrals - not a custom palette.
THEMES = {
    'light': dict(canvas='#ffffff', subtle='#f6f8fa', border='#d0d7de', fg='#1f2328',
                  muted='#656d76', accent=GREEN),
    'dark': dict(canvas='#0d1117', subtle='#161b22', border='#30363d', fg='#e6edf3',
                 muted='#8b949e', accent=GREEN_DARK),
}

# ---- GitHub Linguist language colours ------------------------------------
LANG = {'Python': '#3572A5', 'Rust': '#dea584', 'TypeScript': '#3178c6',
        'JavaScript': '#f1e05a', 'Go': '#00ADD8', 'C': '#555555', 'Vue': '#41b883',
        'Shell': '#89e051', 'Scheme': '#1e4aec', 'SQL': '#e38c00', 'CSS': '#663399',
        'HTML': '#e34c26', 'SCSS': '#c6538c'}

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def accent(theme):
    return THEMES[theme]['accent']


def txt(x, y, s, size=13, fill='fg', weight='400', anchor='start', family=SANS, cls=''):
    c = f' class="{cls}"' if cls else ''
    f = fill if fill.startswith('#') else f'var(--{fill})'
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{f}" text-anchor="{anchor}"{c}>{esc(s)}</text>')


def rect(x, y, w, h, fill=None, stroke=None, rx=0, sw=1, cls='', op=None):
    f = 'none' if fill is None else (fill if fill.startswith('#') else f'var(--{fill})')
    s = ''
    if stroke:
        sv = stroke if stroke.startswith('#') else f'var(--{stroke})'
        s = f' stroke="{sv}" stroke-width="{sw}"'
    c = f' class="{cls}"' if cls else ''
    o = f' fill-opacity="{op}"' if op is not None else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{s}{c}{o}/>'


def icon(kind, name, x, y, size, colour):
    ic = ICONS[kind][name]
    vb = [float(v) for v in ic['vb'].split()]
    scale = size / vb[2]
    f = colour if colour.startswith('#') else f'var(--{colour})'
    paths = ''.join(f'<path d="{d}"/>' for d in ic['d'])
    return f'<g transform="translate({x},{y}) scale({scale:.5f})" fill="{f}">{paths}</g>'


def card(w, h, rx=6):
    return rect(0.5, 0.5, w - 1, h - 1, 'canvas', 'border', rx=rx)


def style(theme):
    t = THEMES[theme]
    v = ';'.join(f'--{k}:{val}' for k, val in t.items())
    return ('<style>'
            f'svg{{{v}}}'
            # the resting state of every animated element is VISIBLE. The motion
            # lives entirely in the keyframes, with fill-mode both, so a block
            # whose animation never starts - browsers defer them for off-screen
            # <img>-embedded SVGs - still renders its content instead of blank.
            '.rise{animation:rise .55s cubic-bezier(.2,.7,.2,1) both}'
            '@keyframes rise{from{opacity:0;transform:translateY(7px)}'
            'to{opacity:1;transform:none}}'
            '.bar{animation:grow 1s cubic-bezier(.2,.75,.2,1) both}'
            '@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
            '.pulse{animation:pulse 2.4s ease-in-out infinite}'
            '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}'
            '@media (prefers-reduced-motion:reduce){'
            '.rise,.bar,.pulse{animation:none;opacity:1;transform:none}}'
            '</style>')


def svg(w, h, label_, theme, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label_)}">{style(theme)}{body}</svg>\n')


def write(name, theme, content):
    d = HERE if theme == 'light' else HERE / 'dark'
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(content)


# =====================================================================
# HEADER
# =====================================================================
def header(theme):
    W, H = 1000, 224
    ac = accent(theme)
    b = [card(W, H)]
    b.append(f'<g class="rise"><circle cx="32" cy="21" r="3.5" fill="{ac}"/>'
             f'{txt(42, 25, "Developer profile", size=11.5, fill="muted")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.05s">'
             f'{txt(28, 62, "RelativelyUnknown", size=28, weight="700")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.09s">'
             f'{txt(28, 86, "Data and AI engineering", size=14, fill="muted")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.13s">'
             f'{txt(28, 122, "I build tools that sit close to the code - static analysis,", size=14)}'
             f'{txt(28, 144, "language grammars, and the editor surfaces around them.", size=14)}</g>')

    for i, (ic, lab) in enumerate([('code-16', 'TypeScript, Python and Rust'),
                                    ('repo-16', '6 public repositories')]):
        y = 174 + i * 24
        b.append(f'<g class="rise" style="animation-delay:{.2 + i * .06:.2f}s">'
                 f'{icon("oc", ic, 28, y - 12, 14, ac)}'
                 f'{txt(50, y, lab, size=13, fill="muted")}</g>')

    stats = [(str(DATA['total']), 'commits, last year'),
             (str(DATA['active_days']), 'active days'),
             (str(DATA['peak']), 'best day')]
    sx, sw = 592, 380
    for i, (n, lab) in enumerate(stats):
        x = sx + i * (sw / 3)
        if i:
            b.append(f'<line x1="{x:.0f}" y1="80" x2="{x:.0f}" y2="180" stroke="var(--border)"/>')
        cx = x + sw / 6
        b.append(f'<g class="rise" style="animation-delay:{.28 + i * .08:.2f}s">'
                 f'{txt(cx, 128, n, size=30, weight="700", anchor="middle")}'
                 f'{txt(cx, 154, lab, size=11.5, fill="muted", anchor="middle")}</g>')
    return svg(W, H, 'RelativelyUnknown - data and AI engineering. I build tools that sit close '
                     'to the code: static analysis, language grammars, and the editor surfaces '
                     f'around them. TypeScript, Python and Rust. {DATA["total"]} commits in the '
                     f'last year across 6 public repositories, on {DATA["active_days"]} active '
                     f'days, peaking at {DATA["peak"]} in one day.',
               theme, ''.join(b))


# =====================================================================
# REPO CARDS
# =====================================================================
def repo_card(theme, name, desc_lines, langs, meta):
    W, H = 326, 190
    ac = accent(theme)
    b = [card(W, H), rect(8, 0.5, W - 16, 3, ac, rx=1.5)]
    b.append(icon('oc', 'repo-16', 20, 26, 15, ac))
    b.append(txt(44, 38, name, size=13, weight='600'))
    b.append(rect(W - 76, 24, 58, 19, None, 'border', rx=9))
    b.append(txt(W - 47, 37, 'Public', size=10.5, fill='muted', anchor='middle'))
    for i, ln in enumerate(desc_lines):
        b.append(txt(20, 68 + i * 17, ln, size=11.5, fill='muted'))

    total = sum(p for _, p in langs) or 1
    bw, off = W - 40, 0.0
    b.append('<g transform="translate(20,108)">')
    for i, (lname, pct) in enumerate(langs):
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="8" rx="2" '
                 f'fill="{LANG.get(lname, "#8b949e")}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0;animation-delay:{.25 + i * .08:.2f}s"/>')
        off += seg
    b.append('</g>')

    lx = 20
    for i, (lname, pct) in enumerate(langs):
        b.append(f'<g class="rise" style="animation-delay:{.4 + i * .06:.2f}s">'
                 f'<circle cx="{lx + 4}" cy="132" r="4" fill="{LANG.get(lname, "#8b949e")}"/>'
                 f'{txt(lx + 12, 136, f"{lname} {pct:g}%", size=9.5, fill="muted")}</g>')
        lx += 78

    b.append(icon('oc', 'history-16', 20, 158, 12, 'muted'))
    b.append(txt(36, 168, meta, size=10.5, fill='muted'))
    return svg(W, H, f'{name} - {" ".join(desc_lines)} '
                     + ', '.join(f'{l} {p}%' for l, p in langs) + f'. {meta}.',
               theme, ''.join(b))


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


def _sankey_data():
    per_repo = {r: c for r, c in DATA['per_repo'].items() if c > 0}
    repo_order = sorted(per_repo, key=per_repo.get, reverse=True)

    lang_flows = {}
    for repo, count in per_repo.items():
        split = DATA['langs'].get(repo)
        lang_flows[repo] = _apply_pct(count, split) if split else {'Other languages': count}

    totals = {}
    for flows in lang_flows.values():
        for lang, v in flows.items():
            totals[lang] = totals.get(lang, 0) + v
    fold_below = max(8, round(sum(totals.values()) * 0.015))
    kept = {k: v for k, v in totals.items() if v >= fold_below}
    folded = sum(v for k, v in totals.items() if v < fold_below)

    lang_order = sorted(kept, key=kept.get, reverse=True)
    if folded > 0:
        lang_order.append('Other languages')
        kept['Other languages'] = kept.get('Other languages', 0) + folded

    col0 = [dict(id='commits', label='Commits', value=sum(per_repo.values()))]
    col1 = [dict(id=r, label=r, value=per_repo[r]) for r in repo_order]
    col2 = [dict(id=lg, label=lg, value=kept[lg]) for lg in lang_order]

    links01 = [('commits', r, per_repo[r]) for r in repo_order]
    links12 = []
    for r in repo_order:
        flows = lang_flows[r]
        for lg in lang_order:
            v = flows.get(lg, 0)
            if lg == 'Other languages':
                v += sum(val for name, val in flows.items() if name not in kept and name != 'Other languages')
            if v > 0:
                links12.append((r, lg, v))
    return [col0, col1, col2], links01 + links12


def sankey(theme):
    columns, links = _sankey_data()
    W, H, pad, node_w, node_gap = 1000, 460, 26, 16, 9
    ac = accent(theme)
    n_cols = len(columns)
    col_gap = (W - 2 * pad - node_w * n_cols) / (n_cols - 1)
    inner_h = H - 2 * pad - 34
    scale = min((inner_h - node_gap * (len(col) - 1)) / sum(n['value'] for n in col)
                for col in columns)

    pos = {}
    for ci, col in enumerate(columns):
        x = pad + ci * (node_w + col_gap)
        y = pad + 34
        for n in col:
            h = n['value'] * scale
            pos[n['id']] = dict(x=x, y0=y, y1=y + h, col=ci, cursor_l=y, cursor_r=y, **n)
            y += h + node_gap

    subtitle = f'{DATA["total"]} commits, last 365 days -> repo -> language'
    b = [card(W, H)]
    b.append(f'<g class="rise">{txt(28, 32, "Commit flow", size=15, weight="600")}'
             f'{txt(W - 28, 32, subtitle, size=11.5, fill="muted", anchor="end")}</g>')

    for i, (src, tgt, val) in enumerate(links):
        s, t = pos[src], pos[tgt]
        h = val * scale
        sy, ty = s['cursor_r'], t['cursor_l']
        s['cursor_r'] += h
        t['cursor_l'] += h
        x0, x1 = s['x'] + node_w, t['x']
        xm = (x0 + x1) / 2
        d = (f'M{x0:.1f},{sy:.1f} C{xm:.1f},{sy:.1f} {xm:.1f},{ty:.1f} {x1:.1f},{ty:.1f} '
             f'L{x1:.1f},{ty + h:.1f} C{xm:.1f},{ty + h:.1f} {xm:.1f},{sy + h:.1f} {x0:.1f},{sy + h:.1f} Z')
        fill = ac if src == 'commits' else 'var(--muted)'
        op = 0.22 if src == 'commits' else 0.14
        b.append(f'<path d="{d}" fill="{fill}" fill-opacity="{op}" class="rise" '
                 f'style="animation-delay:{.15 + i * .02:.2f}s"/>')

    for col in columns:
        for n in col:
            p = pos[n['id']]
            h = p['y1'] - p['y0']
            fill = ac if n['id'] == 'commits' else 'var(--muted)'
            delay = .05 if p['col'] == 0 else .15 + p['col'] * .1
            b.append(f'<g class="rise" style="animation-delay:{delay:.2f}s">')
            b.append(f'<rect x="{p["x"]:.1f}" y="{p["y0"]:.1f}" width="{node_w}" '
                     f'height="{h:.1f}" rx="2" fill="{fill}"/>')
            if p['col'] == 0:
                lx, anchor = p['x'] + node_w / 2, 'middle'
            elif p['col'] == n_cols - 1:
                lx, anchor = p['x'] - 9, 'end'
            else:
                lx, anchor = p['x'] + node_w + 9, 'start'
            ly = p['y0'] + h / 2
            b.append(txt(lx, ly - 3, n['label'], size=11.5, weight='600', anchor=anchor))
            b.append(txt(lx, ly + 11, f'{n["value"]:g}', size=10.5, fill='muted',
                        anchor=anchor, family=MONO))
            b.append('</g>')

    return svg(W, H, f'Commit flow: {DATA["total"]} commits in the last 365 days, from repo to '
                     'language, sized by commits. ' +
                     ', '.join(f'{n["label"]} {n["value"]:g}' for n in columns[1] + columns[2]),
               theme, ''.join(b))


# =====================================================================
# FOOTER
# =====================================================================
def footer(theme):
    W, H = 1000, 76
    ac = accent(theme)
    b = [card(W, H), rect(8, 0.5, W - 16, 3, ac, rx=1.5)]
    b.append(f'<circle cx="32" cy="41" r="5" fill="{ac}" class="pulse"/>')
    b.append(txt(50, 46, 'Open to talk about developer tooling, static analysis, '
                         'and anything AI-adjacent.', size=13.5))
    return svg(W, H, 'Open to talk about developer tooling, static analysis and anything '
                     'AI-adjacent.', theme, ''.join(b))


if __name__ == '__main__':
    repos = [
        ('mallard', 'Mallard',
         ['A VS Code extension that tracks how much',
          'your AI coding assistant costs you.'],
         DATA['langs'].get('Mallard', []), f"{DATA['per_repo'].get('Mallard', 0)} commits by me"),
        ('burnt', 'burnt',
         ['Static analysis for Databricks and Spark',
          'pipelines - one code graph, 110 rules.'],
         DATA['langs'].get('burnt', []), f"{DATA['per_repo'].get('burnt', 0)} commits by me"),
        ('grammar', 'tree-sitter-sql-extended',
         ['A tree-sitter SQL grammar: an ANSI base',
          'plus 22 compiled dialects.'],
         DATA['langs'].get('tree-sitter-sql-extended', []),
         f"{DATA['per_repo'].get('tree-sitter-sql-extended', 0)} commits by me"),
    ]
    for theme in ('light', 'dark'):
        write('header.svg', theme, header(theme))
        for slug, name, desc, langs, meta in repos:
            write(f'repo-{slug}.svg', theme, repo_card(theme, name, desc, langs, meta))
        write('sankey.svg', theme, sankey(theme))
        write('footer.svg', theme, footer(theme))
    n = len(list(HERE.glob('*.svg'))) + len(list((HERE / 'dark').glob('*.svg')))
    print(f'wrote {n} svg files (light + dark)')

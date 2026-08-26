#!/usr/bin/env python3
"""Generate the SVG blocks for the RelativelyUnknown profile README.

A dossier, not a dashboard.

  The bones are still bordered panels and Octicons - it has to feel native
  to github.com. But the corners are cut, not rounded: every panel is a
  clipped-corner plate with a coloured tab in the notch, closer to shipping
  manifests and equipment plating than to Primer's soft cards. Captions run
  in uppercase monospace with tracking, like stencilled spec labels. Repo
  cards trade their language bar for a small glowing radar plot - three or
  four axes, one per language, scaled to that repo's own mix. A barcode
  glyph signs the footer, like a stamp on the last page.

  Colour is still the five saturated hues from the owner's palette sheet,
  not GitHub's blue-and-green.

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
import math
import pathlib
import random

HERE = pathlib.Path(__file__).resolve().parent
ICONS = json.loads((HERE / 'icons.json').read_text())
DATA = json.loads((HERE / 'data.json').read_text())

# ---- the owner's five hues, from the reference palette sheet -------------
HUES = ['#1569FF', '#31DB92', '#FF5831', '#FFD93B', '#FF7BDD']
HUES_DARK = ['#4C8DFF', '#3DE8A0', '#FF7355', '#FFE066', '#FF95E4']

THEMES = {
    'light': dict(canvas='#ffffff', subtle='#FBF9F4', border='#E4DFD3', fg='#1B1D1C',
                  muted='#6B716D',
                  heat=['#F0EBE0', '#FFE9A3', '#FFC44D', '#FF7A45', '#E8365E']),
    'dark': dict(canvas='#0d1117', subtle='#161B22', border='#30363D', fg='#F0F6FC',
                 muted='#9198A1',
                 heat=['#191D24', '#4A3A0F', '#B8721A', '#FF5831', '#FF95E4']),
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


def hues(theme):
    return HUES_DARK if theme == 'dark' else HUES


def txt(x, y, s, size=13, fill='fg', weight='400', anchor='start', family=SANS, cls='', sp=None):
    c = f' class="{cls}"' if cls else ''
    f = fill if fill.startswith('#') else f'var(--{fill})'
    s_attr = f' letter-spacing="{sp}"' if sp is not None else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{f}" text-anchor="{anchor}"{s_attr}{c}>{esc(s)}</text>')


def label(x, y, s, size=10, fill='muted', anchor='start', weight='600'):
    """An uppercase, tracked, monospace spec caption - the dossier's default caption style."""
    return txt(x, y, s.upper(), size=size, fill=fill, weight=weight, anchor=anchor,
               family=MONO, sp='0.06em')


def rect(x, y, w, h, fill=None, stroke=None, rx=0, sw=1, cls=''):
    f = 'none' if fill is None else (fill if fill.startswith('#') else f'var(--{fill})')
    s = ''
    if stroke:
        sv = stroke if stroke.startswith('#') else f'var(--{stroke})'
        s = f' stroke="{sv}" stroke-width="{sw}"'
    c = f' class="{cls}"' if cls else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{s}{c}/>'

def line(x1, y1, x2, y2, stroke='border', sw=1):
    sv = stroke if stroke.startswith('#') else f'var(--{stroke})'
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{sv}" stroke-width="{sw}"/>'


def icon(kind, name, x, y, size, colour):
    ic = ICONS[kind][name]
    vb = [float(v) for v in ic['vb'].split()]
    scale = size / vb[2]
    f = colour if colour.startswith('#') else f'var(--{colour})'
    paths = ''.join(f'<path d="{d}"/>' for d in ic['d'])
    return f'<g transform="translate({x},{y}) scale({scale:.5f})" fill="{f}">{paths}</g>'


def panel(w, h, cut=16):
    """A clipped-corner plate: the dossier's card - straight cuts, no rounding."""
    x0, y0, x1, y1 = 0.5, 0.5, w - 0.5, h - 0.5
    d = (f'M{x0},{y0} L{x1 - cut},{y0} L{x1},{y0 + cut} L{x1},{y1} '
         f'L{x0 + cut},{y1} L{x0},{y1 - cut} Z')
    return f'<path d="{d}" fill="var(--canvas)" stroke="var(--border)"/>'


def corner_tab(w, h, cut, colour):
    """The coloured wedge filling the panel's cut top-right corner."""
    x1, y0 = w - 0.5, 0.5
    d = f'M{x1 - cut},{y0} L{x1},{y0} L{x1},{y0 + cut} Z'
    return f'<path d="{d}" fill="{colour}"/>'


def barcode(x, y, seed, colour, n=18, h=13, unit=2.1):
    """A deterministic barcode glyph, seeded per-block - a signed stamp, not decoration."""
    rnd = random.Random(seed)
    out, cx = [], x
    for _ in range(n):
        w = unit * rnd.choice([0.55, 1.0, 1.0, 1.4, 1.9])
        out.append(f'<rect x="{cx:.1f}" y="{y}" width="{w:.1f}" height="{h}" fill="{colour}"/>')
        cx += w + unit * 0.6
    return ''.join(out), cx - x


def style(theme):
    t = THEMES[theme]
    v = ';'.join(f'--{k}:{val}' for k, val in t.items() if k != 'heat')
    heat = ';'.join(f'--h{i}:{c}' for i, c in enumerate(t['heat']))
    return ('<style>'
            f'svg{{{v};{heat}}}'
            # the resting state of every animated element is VISIBLE. The motion
            # lives entirely in the keyframes, with fill-mode both, so a block
            # whose animation never starts - browsers defer them for off-screen
            # <img>-embedded SVGs - still renders its content instead of blank.
            '.rise{animation:rise .55s cubic-bezier(.2,.7,.2,1) both}'
            '@keyframes rise{from{opacity:0;transform:translateY(7px)}'
            'to{opacity:1;transform:none}}'
            '.bar{animation:grow 1s cubic-bezier(.2,.75,.2,1) both}'
            '@keyframes grow{from{transform:scaleX(0)}to{transform:scaleX(1)}}'
            '.seg{animation:grow .7s cubic-bezier(.2,.75,.2,1) both}'
            '.cell{animation:pop .42s cubic-bezier(.3,1.5,.5,1) both}'
            '@keyframes pop{from{opacity:0;transform:scale(.35)}'
            'to{opacity:1;transform:scale(1)}}'
            '.pulse{animation:pulse 2.4s ease-in-out infinite}'
            '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}'
            '@media (prefers-reduced-motion:reduce){'
            '.rise,.bar,.cell,.seg,.pulse{animation:none;opacity:1;transform:none}}'
            '</style>')


def svg(w, h, label_, theme, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label_)}">{style(theme)}{body}</svg>\n')


def write(name, theme, content):
    d = HERE if theme == 'light' else HERE / 'dark'
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(content)


def colour_bar(x, y, w, theme, h=6, delay=0.0, rx=None):
    """The owner's signature five-segment bar, wiping in left to right."""
    widths = [0.30, 0.16, 0.24, 0.13, 0.17]
    out, off = [], 0.0
    for i, frac in enumerate(widths):
        seg = w * frac
        out.append(f'<rect x="{x + off:.1f}" y="{y}" width="{seg - 4:.1f}" height="{h}" '
                   f'rx="{rx if rx is not None else h / 2}" fill="{hues(theme)[i]}" class="seg" '
                   f'style="transform-origin:{x + off:.1f}px 0;'
                   f'animation-delay:{delay + i * .09:.2f}s"/>')
        off += seg
    return ''.join(out)


def radar(cx, cy, r, items, hue, theme, delay=0.0):
    """A small glowing polygon plot, one axis per language, scaled to this repo's own mix."""
    n = len(items)
    b = []
    for frac in (0.5, 1.0):
        pts = ' '.join(
            f'{cx + r * frac * math.cos(-math.pi / 2 + i * 2 * math.pi / n):.1f},'
            f'{cy + r * frac * math.sin(-math.pi / 2 + i * 2 * math.pi / n):.1f}'
            for i in range(n))
        b.append(f'<polygon points="{pts}" fill="none" stroke="var(--border)" stroke-width="0.75"/>')
    for i in range(n):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        b.append(line(cx, cy, cx + r * math.cos(ang), cy + r * math.sin(ang), sw=0.75))

    maxpct = max(p for _, p in items) or 1
    verts = []
    for i, (_, p) in enumerate(items):
        ang = -math.pi / 2 + i * 2 * math.pi / n
        rad = r * (0.16 + 0.84 * (p / maxpct))
        verts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    poly = ' '.join(f'{x:.1f},{y:.1f}' for x, y in verts)
    b.append(f'<polygon points="{poly}" fill="{hue}" fill-opacity="0.24" stroke="{hue}" '
             f'stroke-width="1.6" stroke-linejoin="round" class="rise" '
             f'style="animation-delay:{delay:.2f}s;transform-origin:{cx}px {cy}px"/>')
    for x, y in verts:
        b.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.1" fill="{hue}"/>')
    return ''.join(b)


# =====================================================================
# HEADER
# =====================================================================
def header(theme):
    W, H = 1000, 252
    hs = hues(theme)
    b = [panel(W, H, 26), corner_tab(W, H, 26, hs[0])]

    b.append(f'<g class="rise">{label(28, 24, "Developer profile", size=10.5)}</g>')
    b.append(f'<g class="rise" style="animation-delay:.05s">'
             f'{txt(28, 60, "RelativelyUnknown", size=30, weight="800")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.09s">'
             f'{txt(28, 85, "Data and AI engineering", size=14.5, fill="muted")}</g>')
    b.append(colour_bar(28, 99, 300, theme, h=6, delay=.16))
    b.append(f'<g class="rise" style="animation-delay:.15s">'
             f'{txt(28, 133, "I build tools that sit close to the code - static analysis,", size=14)}'
             f'{txt(28, 155, "language grammars, and the editor surfaces around them.", size=14)}</g>')

    for i, (ic, lab) in enumerate([('code-16', 'Stack — TypeScript · Python · Rust'),
                                    ('repo-16', '6 public repositories')]):
        y = 185 + i * 24
        b.append(f'<g class="rise" style="animation-delay:{.22 + i * .06:.2f}s">'
                 f'{icon("oc", ic, 28, y - 12, 14, hs[i])}'
                 f'{label(50, y, lab, size=10.5)}</g>')

    px, pw = 596, 376
    b.append(line(px, 62, px + pw, 62, sw=1))
    rows = [(str(DATA['total']), 'Commits · last 365 days'),
            (str(DATA['active_days']), 'Days with a commit'),
            (str(DATA['peak']), 'Peak in one day')]
    for i, (n, lab) in enumerate(rows):
        y0 = 62 + i * 52
        b.append(f'<g class="rise" style="animation-delay:{.3 + i * .08:.2f}s">'
                 f'{rect(px, y0, 4, 52, hs[i])}'
                 f'{txt(px + 24, y0 + 33, n, size=24, weight="700", family=MONO)}'
                 f'{label(px + pw, y0 + 33, lab, size=10, anchor="end")}</g>')
        b.append(line(px, y0 + 52, px + pw, y0 + 52, sw=1))
    return svg(W, H, 'RelativelyUnknown - data and AI engineering. I build tools that sit close '
                     'to the code: static analysis, language grammars, and the editor surfaces '
                     f'around them. TypeScript, Python and Rust. {DATA["total"]} commits in the '
                     f'last year across 6 public repositories, on {DATA["active_days"]} days, '
                     f'peaking at {DATA["peak"]} in one day.',
               theme, ''.join(b))


# =====================================================================
# REPO CARDS
# =====================================================================
def repo_card(theme, slug, name, desc_lines, langs, meta, hue_i):
    W, H = 360, 210
    hue = hues(theme)[hue_i]
    b = [panel(W, H, 16), corner_tab(W, H, 16, hue)]
    b.append(rect(8, 8, W - 100, 3, hue))

    b.append(icon('oc', 'repo-16', 20, 33, 14, hue))
    b.append(txt(42, 34, name, size=13.5, weight='700'))
    b.append(rect(W - 88, 21, 60, 17, None, 'border', rx=0))
    b.append(label(W - 58, 33, 'Public', size=9.5, anchor='middle'))

    for i, ln in enumerate(desc_lines):
        b.append(txt(20, 66 + i * 17, ln, size=11.5, fill='muted'))

    b.append(line(246, 20, 246, 190, sw=1))

    b.append(icon('oc', 'history-16', 20, 180, 12, 'muted'))
    b.append(label(36, 190, meta, size=9.5))

    b.append(radar(300, 84, 38, langs, hue, theme, delay=.2))
    for i, (lname, pct) in enumerate(langs):
        y = 134 + i * 13
        b.append(f'<g class="rise" style="animation-delay:{.42 + i * .06:.2f}s">'
                 f'<rect x="258" y="{y - 6}" width="6" height="6" '
                 f'fill="{LANG.get(lname, "#8b949e")}"/>'
                 f'{label(268, y, f"{lname} {pct:g}%", size=8.7)}</g>')

    return svg(W, H, f'{name} - {" ".join(desc_lines)} '
                     + ', '.join(f'{l} {p}%' for l, p in langs) + f'. {meta}.',
               theme, ''.join(b))


# =====================================================================
# CONTRIBUTION HEATMAP
# =====================================================================
def activity(theme):
    grid, months = DATA['grid'], DATA['months']
    cell, gap = 12, 3
    left, top = 116, 88
    W = left + 52 * (cell + gap) + 28
    H = top + 7 * (cell + gap) + 76
    nz = sorted(c for wk in grid for c in wk if c)
    qs = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)] if nz else [1, 1, 1]
    hs = hues(theme)
    b = [panel(W, H, 22), corner_tab(W, H, 22, hs[2])]

    b.append(icon('oc', 'graph-16', 28, 32, 16, hs[2]))
    b.append(txt(52, 45, f'{DATA["total"]} commits in the last year', size=15, weight='600'))
    b.append(label(W - 28, 45, 'Authored by me, 6 public repositories', size=10, anchor='end'))
    b.append(colour_bar(28, 60, 210, theme, h=4, delay=.1))

    for w, m in months:
        b.append(label(left + w * (cell + gap), top - 8, m, size=9.5))
    for dow, d in ((1, 'Mon'), (3, 'Wed'), (5, 'Fri')):
        b.append(label(left - 12, top + dow * (cell + gap) + cell - 2, d, size=9.5, anchor='end'))

    for w in range(52):
        for dow in range(7):
            c = grid[w][dow]
            lv = 0 if c == 0 else 1 + sum(c > q for q in qs)
            x, y = left + w * (cell + gap), top + dow * (cell + gap)
            b.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" '
                     f'fill="var(--h{lv})" stroke="var(--border)" stroke-width="0.5" '
                     f'stroke-opacity="0.4" class="cell" '
                     f'style="transform-origin:{x + cell / 2}px {y + cell / 2}px;'
                     f'animation-delay:{0.12 + w * 0.013:.2f}s">'
                     f'<title>{c} commits</title></rect>')

    ly = H - 32
    b.append(label(left, ly, 'Less', size=9.5))
    for i in range(5):
        b.append(f'<rect x="{left + 38 + i * 16}" y="{ly - 10}" width="{cell}" height="{cell}" '
                 f'rx="2" fill="var(--h{i})" stroke="var(--border)" stroke-width="0.5" '
                 f'stroke-opacity="0.4"/>')
    b.append(label(left + 124, ly, 'More', size=9.5))
    b.append(f'<circle cx="{W - 186}" cy="{ly - 4}" r="5" fill="{hs[1]}" class="pulse"/>')
    b.append(label(W - 172, ly, f'{DATA["active_days"]} days with a commit', size=9.5))
    return svg(W, H, f'Contribution heatmap: {DATA["total"]} commits authored across 6 public '
                     f'repositories in the last year, on {DATA["active_days"]} active days, '
                     f'peaking at {DATA["peak"]} in one day.',
               theme, ''.join(b))


# =====================================================================
# LANGUAGES
# =====================================================================
def languages(theme):
    langs = DATA['overall_langs']
    W, H = 1000, 160
    hs = hues(theme)
    b = [panel(W, H, 22), corner_tab(W, H, 22, hs[0])]
    b.append(icon('oc', 'code-16', 28, 32, 16, hs[0]))
    b.append(txt(52, 45, 'Languages', size=15, weight='600'))
    b.append(label(W - 28, 45, f'{DATA["lang_repos"]} public repos, '
                                f'{DATA["lang_bytes"] / 1e6:.1f} MB of source',
                   size=10, anchor='end'))

    total = sum(p for _, p in langs) or 1
    bw, off = W - 56, 0.0
    b.append('<g transform="translate(28,66)">')
    for i, (name, pct) in enumerate(langs):
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="12" rx="0" '
                 f'fill="{LANG.get(name, "#8b949e")}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0;animation-delay:{.2 + i * .07:.2f}s"/>')
        off += seg
    b.append('</g>')

    for i, (name, pct) in enumerate(langs[:6]):
        x = 28 + i * 162
        b.append(f'<g class="rise" style="animation-delay:{.35 + i * .05:.2f}s">'
                 f'<rect x="{x}" y="107" width="7" height="7" fill="{LANG.get(name, "#8b949e")}"/>'
                 f'{label(x + 15, 116, name, size=10.5)}'
                 f'{txt(x + 15, 134, f"{pct}%", size=11.5, fill="muted", family=MONO)}</g>')
    return svg(W, H, 'Languages across every public non-fork repository: '
                     + ', '.join(f'{n} {p}%' for n, p in langs), theme, ''.join(b))


# =====================================================================
# FOOTER
# =====================================================================
def footer(theme):
    W, H = 1000, 100
    hs = hues(theme)
    b = [panel(W, H, 20), corner_tab(W, H, 20, hs[3])]
    b.append(colour_bar(8, 9, W - 40, theme, h=4, delay=0, rx=0))
    b.append(f'<circle cx="38" cy="58" r="5" fill="{hs[1]}" class="pulse"/>')
    b.append(txt(56, 63, 'Open to talk about developer tooling, static analysis, '
                         'and anything AI-adjacent.', size=13.5))
    bar_svg, bar_w = barcode(28, 80, 'RelativelyUnknown/footer', 'var(--muted)')
    b.append(bar_svg)
    b.append(icon('oc', 'link-16', W - 244, 50, 16, hs[0]))
    b.append(txt(W - 220, 63, 'linkedin.com/in/jurreandenys', size=13, fill=hs[0], weight='600'))
    return svg(W, H, 'Open to talk about developer tooling, static analysis and anything '
                     'AI-adjacent - linkedin.com/in/jurreandenys', theme, ''.join(b))


if __name__ == '__main__':
    repos = [
        ('mallard', 'Mallard',
         ['A VS Code extension that tracks how much',
          'your AI coding assistant costs you.'],
         DATA['langs']['Mallard'], f"{DATA['per_repo']['Mallard']} commits by me", 0),
        ('burnt', 'burnt',
         ['Static analysis for Databricks and Spark',
          'pipelines - one code graph, 110 rules.'],
         DATA['langs']['burnt'], f"{DATA['per_repo']['burnt']} commits by me", 1),
        ('grammar', 'tree-sitter-sql-extended',
         ['A tree-sitter SQL grammar: an ANSI base',
          'plus 22 compiled dialects.'],
         DATA['langs']['tree-sitter-sql-extended'],
         f"{DATA['per_repo']['tree-sitter-sql-extended']} commits by me", 2),
    ]
    for theme in ('light', 'dark'):
        write('header.svg', theme, header(theme))
        for slug, name, desc, langs, meta, hue_i in repos:
            write(f'repo-{slug}.svg', theme, repo_card(theme, slug, name, desc, langs, meta, hue_i))
        write('activity.svg', theme, activity(theme))
        write('languages.svg', theme, languages(theme))
        write('footer.svg', theme, footer(theme))
    n = len(list(HERE.glob('*.svg'))) + len(list((HERE / 'dark').glob('*.svg')))
    print(f'wrote {n} svg files (light + dark)')

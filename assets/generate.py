#!/usr/bin/env python3
"""Generate the SVG blocks for the RelativelyUnknown profile README.

GitHub's bones, wearing a different coat.

  Structure is Primer: bordered cards, small radii, muted secondary text,
  repo pins, language bars, a contribution heatmap, Octicons. It should
  feel native to github.com.

  Colour is not Primer. The five saturated hues come from the palette
  sheet in the reference board, so the accents, the heatmap ramp and the
  card edges are the owner's, not GitHub's blue-and-green.

Every block is emitted light and dark; the README picks with <picture>
media="(prefers-color-scheme: dark)", the only image theming GitHub honours.

Motion is CSS @keyframes inside each SVG file. GitHub strips <style> from
README HTML but keeps it inside an SVG loaded as an image. Everything is
guarded by prefers-reduced-motion.

Third-party artwork, vendored as path data in icons.json:
  Simple Icons    - CC0-1.0   https://github.com/simple-icons/simple-icons
  Primer Octicons - MIT       https://github.com/primer/octicons

Numbers in data.json are measured, never asserted; rebuild with build_data.py.
"""
import json
import pathlib

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


def txt(x, y, s, size=13, fill='fg', weight='400', anchor='start', family=SANS, cls=''):
    c = f' class="{cls}"' if cls else ''
    f = fill if fill.startswith('#') else f'var(--{fill})'
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="{f}" text-anchor="{anchor}"{c}>{esc(s)}</text>')


def rect(x, y, w, h, fill=None, stroke=None, rx=0, sw=1, cls=''):
    f = 'none' if fill is None else (fill if fill.startswith('#') else f'var(--{fill})')
    s = ''
    if stroke:
        sv = stroke if stroke.startswith('#') else f'var(--{stroke})'
        s = f' stroke="{sv}" stroke-width="{sw}"'
    c = f' class="{cls}"' if cls else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{s}{c}/>'


def icon(kind, name, x, y, size, colour):
    ic = ICONS[kind][name]
    vb = [float(v) for v in ic['vb'].split()]
    scale = size / vb[2]
    f = colour if colour.startswith('#') else f'var(--{colour})'
    paths = ''.join(f'<path d="{d}"/>' for d in ic['d'])
    return f'<g transform="translate({x},{y}) scale({scale:.5f})" fill="{f}">{paths}</g>'


def card(w, h):
    return rect(0.5, 0.5, w - 1, h - 1, 'canvas', 'border', rx=8)


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


def svg(w, h, label, theme, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label)}">{style(theme)}{body}</svg>\n')


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


# =====================================================================
# HEADER
# =====================================================================
def header(theme):
    W, H = 1000, 252
    hs = hues(theme)
    b = [card(W, H)]
    b.append(f'<g class="rise">{txt(28, 66, "RelativelyUnknown", size=32, weight="700")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.07s">'
             f'{txt(28, 93, "Data and AI engineering", size=15, fill="muted")}</g>')
    b.append(colour_bar(28, 108, 300, theme, h=6, delay=.15))
    b.append(f'<g class="rise" style="animation-delay:.14s">'
             f'{txt(28, 152, "I build tools that sit close to the code - static analysis,", size=14)}'
             f'{txt(28, 174, "language grammars, and the editor surfaces around them.", size=14)}</g>')

    for i, (ic, label, y) in enumerate([('code-16', 'TypeScript / Python / Rust', 212),
                                        ('repo-16', '6 public repositories', 236)]):
        b.append(f'<g class="rise" style="animation-delay:{.2 + i * .06:.2f}s">'
                 f'{icon("oc", ic, 28, y - 12, 15, hs[i])}'
                 f'{txt(52, y, label, size=13, fill="muted")}</g>')

    stats = [(str(DATA['total']), 'commits, last year'),
             (str(DATA['active_days']), 'days with commits'),
             (str(DATA['peak']), 'on the busiest day')]
    for i, (n, lab) in enumerate(stats):
        y = 90 + i * 52
        b.append(f'<g class="rise" style="animation-delay:{.26 + i * .08:.2f}s">'
                 f'{rect(600, y - 28, 372, 42, "subtle", "border", rx=7)}'
                 f'{rect(600, y - 28, 4, 42, hs[i])}'
                 f'{txt(620, y, n, size=18, weight="700", family=MONO)}'
                 f'{txt(956, y, lab, size=12, fill="muted", anchor="end")}</g>')
    return svg(W, H, 'RelativelyUnknown - data and AI engineering. I build tools that sit close '
                     'to the code: static analysis, language grammars, and the editor surfaces '
                     f'around them. TypeScript, Python and Rust. {DATA["total"]} commits in the '
                     f'last year across 6 public repositories, on {DATA["active_days"]} days, '
                     f'peaking at {DATA["peak"]} in one day.',
               theme, ''.join(b))


# =====================================================================
# REPO CARDS
# =====================================================================
def repo_card(theme, name, desc_lines, langs, meta, hue_i):
    W, H = 326, 188
    hue = hues(theme)[hue_i]
    b = [card(W, H), rect(8, 0.5, W - 16, 4, hue, rx=2)]
    b.append(icon('oc', 'repo-16', 20, 29, 15, hue))
    b.append(txt(44, 41, name, size=13, weight='600'))
    b.append(rect(W - 76, 27, 58, 19, None, 'border', rx=10))
    b.append(txt(W - 47, 40, 'Public', size=10.5, fill='muted', anchor='middle'))
    for i, ln in enumerate(desc_lines):
        b.append(txt(20, 72 + i * 17, ln, size=11.5, fill='muted'))

    total = sum(p for _, p in langs) or 1
    bw, off = W - 40, 0.0
    b.append('<g transform="translate(20,124)">')
    for i, (lname, pct) in enumerate(langs):
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="9" rx="4.5" '
                 f'fill="{LANG.get(lname, "#8b949e")}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0;animation-delay:{.25 + i * .1:.2f}s"/>')
        off += seg
    b.append('</g>')

    for i, (lname, pct) in enumerate(langs[:3]):
        lx = 20 + i * 98
        b.append(f'<g class="rise" style="animation-delay:{.4 + i * .06:.2f}s">'
                 f'<circle cx="{lx + 4}" cy="156" r="4.5" fill="{LANG.get(lname, "#8b949e")}"/>'
                 f'{txt(lx + 14, 160, f"{lname} {pct}%", size=10, fill="muted")}</g>')

    b.append(icon('oc', 'history-16', 20, 170, 12, 'muted'))
    b.append(txt(36, 180, meta, size=10.5, fill='muted'))
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
    b = [card(W, H)]

    b.append(icon('oc', 'graph-16', 28, 32, 16, hs[2]))
    b.append(txt(52, 45, f'{DATA["total"]} commits in the last year', size=15, weight='600'))
    b.append(txt(W - 28, 45, 'authored by me, across 6 public repositories',
                 size=12, fill='muted', anchor='end'))
    b.append(colour_bar(28, 60, 210, theme, h=4, delay=.1))

    for w, label in months:
        b.append(txt(left + w * (cell + gap), top - 8, label, size=11, fill='muted'))
    for dow, label in ((1, 'Mon'), (3, 'Wed'), (5, 'Fri')):
        b.append(txt(left - 12, top + dow * (cell + gap) + cell - 2, label,
                     size=11, fill='muted', anchor='end'))

    for w in range(52):
        for dow in range(7):
            c = grid[w][dow]
            lv = 0 if c == 0 else 1 + sum(c > q for q in qs)
            x, y = left + w * (cell + gap), top + dow * (cell + gap)
            b.append(f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="3" '
                     f'fill="var(--h{lv})" stroke="var(--border)" stroke-width="0.5" '
                     f'stroke-opacity="0.4" class="cell" '
                     f'style="transform-origin:{x + cell / 2}px {y + cell / 2}px;'
                     f'animation-delay:{0.12 + w * 0.013:.2f}s">'
                     f'<title>{c} commits</title></rect>')

    ly = H - 32
    b.append(txt(left, ly, 'Less', size=11, fill='muted'))
    for i in range(5):
        b.append(f'<rect x="{left + 38 + i * 16}" y="{ly - 10}" width="{cell}" height="{cell}" '
                 f'rx="3" fill="var(--h{i})" stroke="var(--border)" stroke-width="0.5" '
                 f'stroke-opacity="0.4"/>')
    b.append(txt(left + 124, ly, 'More', size=11, fill='muted'))
    b.append(f'<circle cx="{W - 186}" cy="{ly - 4}" r="5" fill="{hs[1]}" class="pulse"/>')
    b.append(txt(W - 172, ly, f'{DATA["active_days"]} days with a commit', size=11, fill='muted'))
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
    b = [card(W, H)]
    b.append(icon('oc', 'code-16', 28, 32, 16, hues(theme)[0]))
    b.append(txt(52, 45, 'Languages', size=15, weight='600'))
    b.append(txt(W - 28, 45, f'{DATA["lang_repos"]} public repositories, '
                             f'{DATA["lang_bytes"] / 1e6:.1f} MB of source',
                 size=12, fill='muted', anchor='end'))

    total = sum(p for _, p in langs) or 1
    bw, off = W - 56, 0.0
    b.append('<g transform="translate(28,66)">')
    for i, (name, pct) in enumerate(langs):
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="12" rx="6" '
                 f'fill="{LANG.get(name, "#8b949e")}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0;animation-delay:{.2 + i * .07:.2f}s"/>')
        off += seg
    b.append('</g>')

    for i, (name, pct) in enumerate(langs[:6]):
        x = 28 + i * 162
        b.append(f'<g class="rise" style="animation-delay:{.35 + i * .05:.2f}s">'
                 f'<circle cx="{x + 5}" cy="112" r="5" fill="{LANG.get(name, "#8b949e")}"/>'
                 f'{txt(x + 17, 116, name, size=12.5, weight="500")}'
                 f'{txt(x + 17, 135, f"{pct}%", size=12, fill="muted", family=MONO)}</g>')
    return svg(W, H, 'Languages across every public non-fork repository: '
                     + ', '.join(f'{n} {p}%' for n, p in langs), theme, ''.join(b))


# =====================================================================
# FOOTER
# =====================================================================
def footer(theme):
    W, H = 1000, 94
    hs = hues(theme)
    b = [card(W, H), colour_bar(8, 0.5, W - 16, theme, h=4, delay=0, rx=2)]
    b.append(f'<circle cx="38" cy="54" r="5" fill="{hs[1]}" class="pulse"/>')
    b.append(txt(56, 59, 'Open to talk about developer tooling, static analysis, '
                         'and anything AI-adjacent.', size=13.5))
    b.append(icon('oc', 'link-16', W - 244, 46, 16, hs[0]))
    b.append(txt(W - 220, 59, 'linkedin.com/in/jurreandenys', size=13, fill=hs[0], weight='600'))
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
            write(f'repo-{slug}.svg', theme, repo_card(theme, name, desc, langs, meta, hue_i))
        write('activity.svg', theme, activity(theme))
        write('languages.svg', theme, languages(theme))
        write('footer.svg', theme, footer(theme))
    n = len(list(HERE.glob('*.svg'))) + len(list((HERE / 'dark').glob('*.svg')))
    print(f'wrote {n} svg files (light + dark)')

#!/usr/bin/env python3
"""Generate the SVG blocks for the RelativelyUnknown profile README.

GitHub's bones, a terminal's texture.

  Structure is Primer: bordered cards, rounded corners, muted secondary
  text, repo pins, a language bar, Octicons. It should feel native to
  github.com first. But every number sits inside a small dark module
  screen, prompts are prefixed like a shell ("$ whoami"), and colour is
  never a flat fill where a halftone can stand in for it instead - an
  ordered dither, the way a low-colour terminal or a printed dot-gradient
  fakes a tone it doesn't have. Screens get faint scanlines. It's GitHub
  with an ASCII accent, not an ASCII page - most of the type is still
  plain sans, most of the chrome is still a bordered card.

  Colour is not Primer. The five hues come from the palette sheet in the
  reference board, but they show up sparingly now - a dithered strip, a
  thin edge, a single accent tick - not as the loudest thing on the page.
  Module screens are always dark, light theme or dark, because a screen
  is a screen.

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
import random

HERE = pathlib.Path(__file__).resolve().parent
ICONS = json.loads((HERE / 'icons.json').read_text())
DATA = json.loads((HERE / 'data.json').read_text())

# ---- the owner's five hues, from the reference palette sheet -------------
HUES = ['#1569FF', '#31DB92', '#FF5831', '#FFD93B', '#FF7BDD']
HUES_DARK = ['#4C8DFF', '#3DE8A0', '#FF7355', '#FFE066', '#FF95E4']

# a module screen is always this dark, in either site theme - it's a screen
SCREEN_BG = '#12141A'
SCREEN_MUTED = '#828B99'
SCREEN_FG = '#E8EAED'

# ordered dithering: a 4x4 Bayer matrix, used to fake a tone out of one flat colour
BAYER4 = [[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]

THEMES = {
    'light': dict(canvas='#ffffff', subtle='#FBF9F4', border='#E4DFD3', fg='#1B1D1C',
                  muted='#6B716D'),
    'dark': dict(canvas='#0d1117', subtle='#161B22', border='#30363D', fg='#F0F6FC',
                 muted='#9198A1'),
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


def cap(x, y, s, size=8.5, fill=SCREEN_MUTED, anchor='start'):
    """A stencilled capital label, as printed on a module's screen."""
    return txt(x, y, s.upper(), size=size, fill=fill, weight='600', anchor=anchor,
               family=MONO, sp='0.07em')


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


def card(w, h, rx=10):
    return rect(0.5, 0.5, w - 1, h - 1, 'canvas', 'border', rx=rx)


def screen(x, y, w, h, rx=8):
    """A module's display - flat, dark, no bezel. A screen is a screen in any theme."""
    return rect(x, y, w, h, SCREEN_BG, rx=rx)


def dither(x, y, w, h, cell, colour, density=0.6, fill_frac=0.72):
    """An ordered-dither patch: a flat colour faked as a halftone, Bayer-matrix style."""
    cols, rows = max(1, round(w / cell)), max(1, round(h / cell))
    s = cell * fill_frac
    out = []
    for r in range(rows):
        for c in range(cols):
            t = (BAYER4[r % 4][c % 4] + 0.5) / 16
            if density > t:
                cx, cy = x + c * cell + cell / 2, y + r * cell + cell / 2
                out.append(f'<rect x="{cx - s / 2:.1f}" y="{cy - s / 2:.1f}" '
                           f'width="{s:.1f}" height="{s:.1f}" fill="{colour}"/>')
    return ''.join(out)


def scanlines(x, y, w, h, gap=4, colour='#ffffff', opacity=0.045):
    """Faint horizontal lines across a screen - the CRT texture a module display carries."""
    out, yy = [], y + gap
    while yy < y + h:
        out.append(f'<line x1="{x}" y1="{yy:.1f}" x2="{x + w}" y2="{yy:.1f}" '
                   f'stroke="{colour}" stroke-width="1" opacity="{opacity}"/>')
        yy += gap
    return ''.join(out)


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
            '.seg{animation:grow .7s cubic-bezier(.2,.75,.2,1) both}'
            '.pulse{animation:pulse 2.4s ease-in-out infinite}'
            '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}'
            '@media (prefers-reduced-motion:reduce){'
            '.rise,.bar,.seg,.pulse{animation:none;opacity:1;transform:none}}'
            '</style>')


def svg(w, h, label_, theme, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label_)}">{style(theme)}{body}</svg>\n')


def write(name, theme, content):
    d = HERE if theme == 'light' else HERE / 'dark'
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(content)


def colour_bar(x, y, w, theme, h=9, delay=0.0):
    """The owner's signature five-segment bar - dithered halftone, not a flat fill."""
    widths = [0.30, 0.16, 0.24, 0.13, 0.17]
    out, off = [], 0.0
    for i, frac in enumerate(widths):
        seg = w * frac
        dots = dither(x + off, y, seg - 4, h, cell=2.3, colour=hues(theme)[i], density=0.62)
        out.append(f'<g class="seg" style="transform-origin:{x + off:.1f}px {y}px;'
                   f'animation-delay:{delay + i * .09:.2f}s">{dots}</g>')
        off += seg
    return ''.join(out)


def stat_module(x, y, w, h, value, cap_text, hue, delay=0.0):
    """A terminal-style parameter readout: a dithered icon, a tracked label, a mono value."""
    b = [screen(x, y, w, h), scanlines(x + 3, y + 3, w - 6, h - 6)]
    b.append(dither(x + 10, y + 11, 12, 12, cell=3, colour=hue, density=0.72))
    b.append(cap(x + 29, y + 20, cap_text))
    b.append(txt(x + 13, y + h - 15, value, size=25, weight='700', fill=SCREEN_FG, family=MONO))
    b.append(rect(x + 13, y + h - 9, 20, 3, hue))
    return f'<g class="rise" style="animation-delay:{delay:.2f}s">{"".join(b)}</g>'


def lang_screen(x, y, w, h, langs, delay=0.0):
    """A module readout of a repo's language mix - one row per language, Linguist colours."""
    b = [screen(x, y, w, h), scanlines(x + 3, y + 3, w - 6, h - 6)]
    rh = h / len(langs)
    for i, (name, pct) in enumerate(langs):
        ry = y + rh * i + rh / 2 + 3
        colour = LANG.get(name, '#8b949e')
        b.append(f'<g class="rise" style="animation-delay:{delay + i * .06:.2f}s">'
                 f'<rect x="{x + 12}" y="{ry - 8}" width="7" height="7" rx="1.5" fill="{colour}"/>'
                 f'{cap(x + 25, ry, name)}'
                 f'{txt(x + w - 12, ry, f"{pct:g}%", size=10.5, weight="700", fill=colour, anchor="end", family=MONO)}'
                 f'</g>')
    return ''.join(b)


def waveform(x, y, w, h, seed, colour, n=22):
    """A small signal trace, the way a module screen shows a live level - a closing flourish."""
    rnd = random.Random(seed)
    bw = w / n
    out = []
    for i in range(n):
        bh = h * (0.18 + 0.82 * rnd.random())
        bx = x + i * bw
        by = y + (h - bh) / 2
        out.append(f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw * 0.55:.1f}" height="{bh:.1f}" '
                   f'rx="{bw * 0.25:.1f}" fill="{colour}"/>')
    return ''.join(out)


# =====================================================================
# HEADER
# =====================================================================
def header(theme):
    W, H = 1000, 252
    hs = hues(theme)
    b = [card(W, H)]
    b.append(f'<g class="rise">{txt(28, 24, "$ whoami", size=11, fill="muted", family=MONO, sp="0.03em")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.05s">'
             f'{txt(28, 60, "RelativelyUnknown", size=30, weight="800")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.09s">'
             f'{txt(28, 85, "Data and AI engineering", size=14.5, fill="muted")}</g>')
    b.append(colour_bar(28, 100, 300, theme, delay=.16))
    b.append(f'<g class="rise" style="animation-delay:.15s">'
             f'{txt(28, 138, "I build tools that sit close to the code - static analysis,", size=14)}'
             f'{txt(28, 160, "language grammars, and the editor surfaces around them.", size=14)}</g>')

    for i, lab in enumerate(['$ stack   typescript, python, rust',
                              '$ repos   6 public']):
        y = 188 + i * 22
        b.append(f'<g class="rise" style="animation-delay:{.22 + i * .06:.2f}s">'
                 f'{txt(28, y, lab, size=12, fill="muted", family=MONO)}</g>')

    mods = [(str(DATA['total']), 'commits'),
            (str(DATA['active_days']), 'active days'),
            (str(DATA['peak']), 'best day')]
    mw, gap, mx = 118, 13, 592
    for i, (val, lab) in enumerate(mods):
        x = mx + i * (mw + gap)
        b.append(stat_module(x, 64, mw, 156, val, lab, hs[i], delay=.28 + i * .08))
    return svg(W, H, 'RelativelyUnknown - data and AI engineering. I build tools that sit close '
                     'to the code: static analysis, language grammars, and the editor surfaces '
                     f'around them. TypeScript, Python and Rust. {DATA["total"]} commits in the '
                     f'last year across 6 public repositories, on {DATA["active_days"]} active '
                     f'days, peaking at {DATA["peak"]} in one day.',
               theme, ''.join(b))


# =====================================================================
# REPO CARDS
# =====================================================================
def repo_card(theme, name, desc_lines, langs, meta, hue_i):
    W, H = 326, 196
    hue = hues(theme)[hue_i]
    b = [card(W, H)]
    b.append(dither(8, 1, W - 16, 4, cell=2, colour=hue, density=0.68))
    b.append(icon('oc', 'repo-16', 20, 29, 15, hue))
    b.append(txt(44, 41, name, size=13, weight='600'))
    b.append(rect(W - 76, 27, 58, 19, None, 'border', rx=9))
    b.append(txt(W - 47, 40, 'Public', size=10.5, fill='muted', anchor='middle'))
    for i, ln in enumerate(desc_lines):
        b.append(txt(20, 72 + i * 17, ln, size=11.5, fill='muted'))

    b.append(lang_screen(20, 112, W - 40, 15 * len(langs) + 10, langs, delay=.3))

    b.append(icon('oc', 'history-16', 20, 180, 12, 'muted'))
    b.append(txt(36, 190, meta, size=10.5, fill='muted'))
    return svg(W, H, f'{name} - {" ".join(desc_lines)} '
                     + ', '.join(f'{l} {p}%' for l, p in langs) + f'. {meta}.',
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
    b.append(txt(W - 28, 45, f'$ {DATA["lang_repos"]} public repos, '
                             f'{DATA["lang_bytes"] / 1e6:.1f} MB source',
                 size=11.5, fill='muted', anchor='end', family=MONO))

    total = sum(p for _, p in langs) or 1
    bw, off = W - 56, 0.0
    b.append('<g transform="translate(28,66)">')
    for i, (name, pct) in enumerate(langs):
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="12" rx="3" '
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
    b = [card(W, H), colour_bar(8, 1, W - 16, theme, h=7, delay=0)]
    b.append(f'<circle cx="38" cy="54" r="5" fill="{hs[1]}" class="pulse"/>')
    b.append(txt(56, 59, 'Open to talk about developer tooling, static analysis, '
                         'and anything AI-adjacent.', size=13.5))
    b.append(screen(W - 148, 30, 120, 34, rx=7))
    b.append(scanlines(W - 145, 33, 114, 28))
    b.append(waveform(W - 140, 38, 104, 18, 'RelativelyUnknown/footer', 'var(--muted)'))
    return svg(W, H, 'Open to talk about developer tooling, static analysis and anything '
                     'AI-adjacent.', theme, ''.join(b))


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
        write('languages.svg', theme, languages(theme))
        write('footer.svg', theme, footer(theme))
    n = len(list(HERE.glob('*.svg'))) + len(list((HERE / 'dark').glob('*.svg')))
    print(f'wrote {n} svg files (light + dark)')

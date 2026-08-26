#!/usr/bin/env python3
"""Generate the SVG blocks for the RelativelyUnknown profile README.

Design follows GitHub's own Primer system so the page sits inside github.com
rather than on top of it: Primer colour tokens, 6px radii, 1px borders, repo
cards, language bars, Linguist language colours, a contribution heatmap, and
Octicons.

Every block is emitted twice — light and dark — and the README picks between
them with <picture media="(prefers-color-scheme: dark)">, which is the only
theming mechanism GitHub honours for images.

Motion is CSS @keyframes inside each SVG file. GitHub strips <style> from
README HTML, but keeps it inside an SVG loaded as an image. Every animation
is guarded by prefers-reduced-motion.

Third-party artwork, vendored as path data in icons.json:
  Simple Icons    - CC0-1.0   https://github.com/simple-icons/simple-icons
  Primer Octicons - MIT       https://github.com/primer/octicons
Brand marks remain trademarks of their respective owners.

Numbers in data.json come from the git history of the repositories and from
their working trees; regenerate them with build_data.py.
"""
import json
import pathlib

HERE = pathlib.Path(__file__).resolve().parent
ICONS = json.loads((HERE / 'icons.json').read_text())
DATA = json.loads((HERE / 'data.json').read_text())
BRAND = json.loads((HERE / 'si-colours.json').read_text())


def _lum(hex_colour):
    r, g, b = (int(hex_colour[i:i + 2], 16) / 255 for i in (1, 3, 5))
    f = lambda c: c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4
    return .2126 * f(r) + .7152 * f(g) + .0722 * f(b)


def brand(slug, theme):
    """Brand colour, falling back to the foreground where it would vanish
    into the canvas (Rust, pandas and NumPy are near-black)."""
    c = BRAND.get(slug)
    if not c:
        return 'fg'
    lum = _lum(c)
    if theme == 'dark' and lum < 0.16:
        return 'fg'
    if theme == 'light' and lum > 0.75:
        return 'fg'
    return c

# ---- Primer colour tokens -------------------------------------------------
THEMES = {
    'light': dict(canvas='#ffffff', subtle='#f6f8fa', border='#d1d9e0', fg='#1f2328',
                  muted='#59636e', accent='#0969da', success='#1a7f37',
                  heat=['#eff2f5', '#aceebb', '#4ac26b', '#2da44e', '#116329']),
    'dark': dict(canvas='#0d1117', subtle='#151b23', border='#3d444d', fg='#f0f6fc',
                 muted='#9198a1', accent='#4493f8', success='#3fb950',
                 heat=['#151b23', '#033a16', '#196c2e', '#2ea043', '#56d364']),
}

# ---- GitHub Linguist language colours ------------------------------------
LANG = {'Python': '#3572A5', 'Rust': '#dea584', 'TypeScript': '#3178c6',
        'JavaScript': '#f1e05a', 'Go': '#00ADD8', 'C': '#555555', 'Vue': '#41b883',
        'Shell': '#89e051', 'Scheme': '#1e4aec', 'SQL': '#e38c00'}

SANS = ("-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif")
MONO = "ui-monospace,SFMono-Regular,'SF Mono',Menlo,Consolas,'Liberation Mono',monospace"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def txt(x, y, s, size=13, fill='fg', weight='400', anchor='start', family=SANS, cls=''):
    c = f' class="{cls}"' if cls else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" '
            f'font-weight="{weight}" fill="var(--{fill})" text-anchor="{anchor}"{c}>'
            f'{esc(s)}</text>')


def rect(x, y, w, h, fill=None, stroke=None, rx=0, sw=1, cls=''):
    f = 'none' if fill is None else f'var(--{fill})'
    s = f' stroke="var(--{stroke})" stroke-width="{sw}"' if stroke else ''
    c = f' class="{cls}"' if cls else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}"{s}{c}/>'


def icon(kind, name, x, y, size, colour):
    """Place a vendored Simple Icon or Octicon, scaled and recoloured."""
    ic = ICONS[kind][name]
    vb = [float(v) for v in ic['vb'].split()]
    scale = size / vb[2]
    fill = colour if colour.startswith('#') else f'var(--{colour})'
    paths = ''.join(f'<path d="{d}"/>' for d in ic['d'])
    return f'<g transform="translate({x},{y}) scale({scale:.5f})" fill="{fill}">{paths}</g>'


def card(w, h):
    return rect(0.5, 0.5, w - 1, h - 1, 'canvas', 'border', rx=6)


def style(theme):
    t = THEMES[theme]
    vars_ = ';'.join(f'--{k}:{v}' for k, v in t.items() if k != 'heat')
    heat = ';'.join(f'--h{i}:{c}' for i, c in enumerate(t['heat']))
    return ('<style>'
            f'svg{{{vars_};{heat}}}'
            '.rise{opacity:0;animation:rise .5s cubic-bezier(.2,.7,.2,1) forwards}'
            '@keyframes rise{from{opacity:0;transform:translateY(6px)}'
            'to{opacity:1;transform:translateY(0)}}'
            '.bar{transform:scaleX(0);animation:grow .9s cubic-bezier(.2,.7,.2,1) .25s forwards}'
            '@keyframes grow{to{transform:scaleX(1)}}'
            '.cell{opacity:0;animation:pop .32s ease-out forwards}'
            '@keyframes pop{from{opacity:0}to{opacity:1}}'
            '.pulse{animation:pulse 2.6s ease-in-out infinite}'
            '@keyframes pulse{0%,100%{opacity:1}50%{opacity:.4}}'
            '@media (prefers-reduced-motion:reduce){'
            '.rise,.bar,.cell,.pulse{animation:none;opacity:1;transform:none}}'
            '</style>')


def svg(w, h, label, theme, body):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label)}">'
            f'{style(theme)}{body}</svg>\n')


def write(name, theme, content):
    d = HERE if theme == 'light' else HERE / 'dark'
    d.mkdir(parents=True, exist_ok=True)
    (d / name).write_text(content)


# =====================================================================
# HEADER
# =====================================================================
def header(theme):
    W, H = 1000, 236
    b = [card(W, H)]
    b.append(f'<g class="rise">{txt(28, 62, "RelativelyUnknown", size=30, weight="600")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.06s">'
             f'{txt(28, 88, "Data and AI engineering", size=15, fill="muted")}</g>')
    b.append(f'<g class="rise" style="animation-delay:.12s">'
             f'{txt(28, 124, "I build tools that sit close to the code - static analysis,", size=14)}'
             f'{txt(28, 146, "language grammars, and the editor surfaces around them.", size=14)}</g>')

    for i, (ic, label, y) in enumerate([('code-16', 'TypeScript / Rust / Python', 186),
                                        ('repo-16', '3 public projects', 210)]):
        b.append(f'<g class="rise" style="animation-delay:{.18 + i * .06:.2f}s">'
                 f'{icon("oc", ic, 28, y - 12, 15, "muted")}'
                 f'{txt(52, y, label, size=13, fill="muted")}</g>')

    stats = [(str(DATA['total']), 'commits, last year'),
             (str(DATA['active_days']), 'days with commits'),
             (str(len(DATA['langs'])), 'projects shipped')]
    for i, (n, lab) in enumerate(stats):
        y = 84 + i * 48
        b.append(f'<g class="rise" style="animation-delay:{.24 + i * .07:.2f}s">'
                 f'{rect(660, y - 26, 312, 40, "subtle", "border", rx=6)}'
                 f'{txt(676, y, n, size=17, weight="600", family=MONO)}'
                 f'{txt(956, y, lab, size=12, fill="muted", anchor="end")}</g>')
    return svg(W, H, 'RelativelyUnknown - data and AI engineering. I build tools that sit close '
                     'to the code: static analysis, language grammars, and editor tooling.',
               theme, ''.join(b))


# =====================================================================
# REPO CARDS
# =====================================================================
def repo_card(theme, name, desc_lines, langs, meta):
    W, H = 326, 182
    b = [card(W, H)]
    b.append(icon('oc', 'repo-16', 16, 18, 16, 'muted'))
    b.append(txt(40, 31, name, size=13.5, weight='600', fill='accent'))
    b.append(rect(W - 74, 17, 58, 20, None, 'border', rx=10))
    b.append(txt(W - 45, 31, 'Public', size=11, fill='muted', anchor='middle'))
    for i, ln in enumerate(desc_lines):
        b.append(txt(16, 60 + i * 18, ln, size=12, fill='muted'))

    total = sum(p for _, p in langs) or 1
    bw = W - 32
    b.append('<g transform="translate(16,120)">')
    off = 0.0
    for lname, pct in langs:
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="8" rx="4" '
                 f'fill="{LANG.get(lname, "#8b949e")}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0"/>')
        off += seg
    b.append('</g>')

    for i, (lname, pct) in enumerate(langs[:3]):
        lx = 16 + i * 104
        b.append(f'<circle cx="{lx + 5}" cy="150" r="5" fill="{LANG.get(lname, "#8b949e")}"/>')
        b.append(txt(lx + 16, 154, f'{lname} {pct}%', size=10.5, fill='muted'))

    b.append(icon('oc', 'history-16', 16, 164, 13, 'muted'))
    b.append(txt(34, 175, meta, size=10.5, fill='muted'))
    return svg(W, H, f'{name} - {" ".join(desc_lines)} {meta}', theme, ''.join(b))


# =====================================================================
# CONTRIBUTION HEATMAP
# =====================================================================
def activity(theme):
    grid, months = DATA['grid'], DATA['months']
    cell, gap = 12, 3
    left, top = 116, 78
    W = left + 52 * (cell + gap) + 28
    H = top + 7 * (cell + gap) + 74
    nz = sorted(c for wk in grid for c in wk if c)
    qs = [nz[int(len(nz) * f)] for f in (0.25, 0.5, 0.75)] if nz else [1, 1, 1]
    b = [card(W, H)]

    b.append(icon('oc', 'graph-16', 28, 32, 16, 'muted'))
    b.append(txt(52, 45, f'{DATA["total"]} commits in the last year', size=15, weight='600'))
    b.append(txt(W - 28, 45, 'authored by me, across 4 public repositories',
                 size=12, fill='muted', anchor='end'))

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
                     f'stroke-opacity="0.35" class="cell" '
                     f'style="animation-delay:{0.15 + w * 0.012:.2f}s">'
                     f'<title>{c} commits</title></rect>')

    ly = H - 32
    b.append(txt(left, ly, 'Less', size=11, fill='muted'))
    for i in range(5):
        b.append(f'<rect x="{left + 38 + i * 16}" y="{ly - 10}" width="{cell}" height="{cell}" '
                 f'rx="3" fill="var(--h{i})" stroke="var(--border)" stroke-width="0.5" '
                 f'stroke-opacity="0.35"/>')
    b.append(txt(left + 124, ly, 'More', size=11, fill='muted'))
    b.append(f'<circle cx="{W - 168}" cy="{ly - 4}" r="4" fill="var(--success)" class="pulse"/>')
    b.append(txt(W - 156, ly, f'busiest day: {DATA["peak"]} commits', size=11, fill='muted'))
    return svg(W, H, f'Contribution heatmap: {DATA["total"]} commits authored across 4 public '
                     f'repositories in the last year, on {DATA["active_days"]} active days.',
               theme, ''.join(b))


# =====================================================================
# STACK
# =====================================================================
def stack(theme):
    groups = [
        ('Languages', [('TypeScript', 'typescript'), ('Python', 'python'), ('Rust', 'rust'),
                       ('JavaScript', 'javascript'), ('SQL', 'postgresql')]),
        ('Data and models', [('PyTorch', 'pytorch'), ('TensorFlow', 'tensorflow'),
                             ('scikit-learn', 'scikitlearn'), ('pandas', 'pandas'),
                             ('NumPy', 'numpy')]),
        ('Platform', [('Spark', 'apachespark'), ('Databricks', 'databricks'),
                      ('PostgreSQL', 'postgresql'), ('MySQL', 'mysql'), ('Grafana', 'grafana')]),
        ('Infrastructure', [('Docker', 'docker'), ('Kubernetes', 'kubernetes'),
                            ('Linux', 'linux'), ('Git', 'git'),
                            ('GitHub Actions', 'githubactions')]),
    ]
    tw, th, gap = 172, 40, 10
    W = 28 * 2 + 5 * tw + 4 * gap
    rowh = 34 + th + 20
    H = 64 + len(groups) * rowh
    b = [card(W, H)]
    b.append(icon('oc', 'terminal-16', 28, 32, 16, 'muted'))
    b.append(txt(52, 45, 'Stack', size=15, weight='600'))
    b.append(txt(W - 28, 45, 'reached for most often', size=12, fill='muted', anchor='end'))

    n = 0
    for gi, (gname, items) in enumerate(groups):
        gy = 66 + gi * rowh
        b.append(txt(28, gy + 14, gname.upper(), size=10, fill='muted', family=MONO))
        for i, (label, slug) in enumerate(items):
            x, y = 28 + i * (tw + gap), gy + 26
            b.append(f'<g class="rise" style="animation-delay:{.1 + n * .025:.2f}s">'
                     f'{rect(x, y, tw, th, "subtle", "border", rx=6)}'
                     f'{icon("si", slug, x + 12, y + 11, 18, brand(slug, theme))}'
                     f'{txt(x + 40, y + 25, label, size=12.5, weight="500")}</g>')
            n += 1
    return svg(W, H, 'Stack: TypeScript, Python, Rust, JavaScript, SQL; PyTorch, TensorFlow, '
                     'scikit-learn, pandas, NumPy; Spark, Databricks, PostgreSQL, MySQL, '
                     'Grafana; Docker, Kubernetes, Linux, Git, GitHub Actions.',
               theme, ''.join(b))


# =====================================================================
# LANGUAGES - measured across every non-fork repository
# =====================================================================
def languages(theme):
    langs = DATA['overall_langs']
    W, H = 1000, 150
    b = [card(W, H)]
    b.append(icon('oc', 'code-16', 28, 32, 16, 'muted'))
    b.append(txt(52, 45, 'Languages', size=15, weight='600'))
    b.append(txt(W - 28, 45, f'{DATA["lang_repos"]} repositories, '
                             f'{DATA["lang_bytes"] / 1e6:.1f} MB of source',
                 size=12, fill='muted', anchor='end'))

    total = sum(p for _, p in langs) or 1
    bw, off = W - 56, 0.0
    b.append('<g transform="translate(28,70)">')
    for name, pct in langs:
        seg = bw * pct / total
        b.append(f'<rect x="{off:.1f}" y="0" width="{max(seg - 2, 2):.1f}" height="10" rx="5" '
                 f'fill="{LANG.get(name, "#8b949e")}" class="bar" '
                 f'style="transform-origin:{off:.1f}px 0"/>')
        off += seg
    b.append('</g>')

    for i, (name, pct) in enumerate(langs[:6]):
        x = 28 + i * 162
        b.append(f'<g class="rise" style="animation-delay:{.3 + i * .05:.2f}s">'
                 f'<circle cx="{x + 5}" cy="106" r="5" fill="{LANG.get(name, "#8b949e")}"/>'
                 f'{txt(x + 17, 110, name, size=12, weight="500")}'
                 f'{txt(x + 17, 128, f"{pct}%", size=11.5, fill="muted", family=MONO)}</g>')
    return svg(W, H, 'Languages across every non-fork repository: '
                     + ', '.join(f'{n} {p}%' for n, p in langs), theme, ''.join(b))


# =====================================================================
# FOOTER
# =====================================================================
def footer(theme):
    W, H = 1000, 78
    b = [card(W, H)]
    b.append('<circle cx="34" cy="39" r="5" fill="var(--success)" class="pulse"/>')
    b.append(txt(50, 44, 'Open to talk about developer tooling, static analysis, '
                         'and anything AI-adjacent.', size=13.5))
    b.append(icon('oc', 'link-16', W - 236, 31, 16, 'accent'))
    b.append(txt(W - 212, 44, 'linkedin.com/in/jurreandenys', size=13, fill='accent',
                 weight='500'))
    return svg(W, H, 'Open to talk - linkedin.com/in/jurreandenys', theme, ''.join(b))


if __name__ == '__main__':
    repos = [
        ('mallard', 'Mallard',
         ['A VS Code extension that tracks how much your',
          'AI coding assistant is actually costing you.'],
         DATA['langs']['Mallard'], f"{DATA['per_repo']['Mallard']} commits by me"),
        ('burnt', 'burnt',
         ['Static analysis for Databricks and Spark',
          'pipelines - one code graph, 110 rules.'],
         DATA['langs']['burnt'], f"{DATA['per_repo']['burnt']} commits by me"),
        ('grammar', 'tree-sitter-sql-extended',
         ['A tree-sitter SQL grammar: an ANSI base plus',
          '22 independently compiled dialects.'],
         DATA['langs']['tree-sitter-sql-extended'],
         f"{DATA['per_repo']['tree-sitter-sql-extended']} commits by me"),
    ]
    for theme in ('light', 'dark'):
        write('header.svg', theme, header(theme))
        for slug, name, desc, langs, meta in repos:
            write(f'repo-{slug}.svg', theme, repo_card(theme, name, desc, langs, meta))
        write('activity.svg', theme, activity(theme))
        write('languages.svg', theme, languages(theme))
        write('stack.svg', theme, stack(theme))
        write('footer.svg', theme, footer(theme))
    n = len(list(HERE.glob('*.svg'))) + len(list((HERE / 'dark').glob('*.svg')))
    print(f'wrote {n} svg files (light + dark)')

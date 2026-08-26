#!/usr/bin/env python3
"""SVG blocks for the RelativelyUnknown profile README.

ONE SYSTEM, held to deliberately narrow rules so the page reads as a single
object rather than a pile of ideas:

  GROUND    one dark warm brown-black, everywhere
  PALETTE   five saturated hues, lifted verbatim from the palette sheet in
            the reference set, plus cream. Nothing else, ever.
  MARKS     circle, ring, capsule, round-capped stroke. That is the entire
            shape vocabulary — no hairlines, no grids, no rulers, no texture.
  CONTRAST  cream marks on colour; dark text on filled colour; cream text on
            the ground. Never a third combination.
  TYPE      one bold sans for names and numerals, one mono for small caps.

Structure comes from the reference set's dominant device: a flat colour panel
carrying one simple mark, captioned beneath (the law-card grid), sequenced and
numbered (the shape-sequence strips), with a tile grid where colour marks
frequency rather than decorating (the widget grids).
"""
import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parent

# ---- palette: taken directly from the reference palette sheet -------------
BG     = '#1A1410'   # dark warm brown-black ground
CREAM  = '#F8F3E0'
GREEN  = '#31DB92'
YELLOW = '#FFD93B'
VERM   = '#FF5831'
BLUE   = '#1569FF'
PINK   = '#FF7BDD'

HUES = [GREEN, YELLOW, VERM, BLUE, PINK]

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def head(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label)}">')


def txt(x, y, s, size=12, fill=CREAM, family=MONO, weight='400', anchor='start', ls=0, op=None):
    o = f' opacity="{op}"' if op is not None else ''
    l = f' letter-spacing="{ls}"' if ls else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{l}{o}>{esc(s)}</text>')


def box(x, y, w, h, fill, rx=0, stroke=None, sw=2, op=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op is not None else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{o}/>'


def dot(cx, cy, r, fill):
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"/>'


def ring(cx, cy, r, stroke, sw=12):
    return (f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="none" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')


def stroke_line(x1, y1, x2, y2, colour, sw=12):
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{colour}" '
            f'stroke-width="{sw}" stroke-linecap="round"/>')


def capsule(x, y, w, h, fill):
    return box(x, y, w, h, fill, rx=min(w, h) / 2)


def arc(cx, cy, r, a0, a1, colour, sw=12):
    """Round-capped arc, angles in degrees clockwise from 12 o'clock."""
    def pt(a):
        rad = math.radians(a - 90)
        return cx + math.cos(rad) * r, cy + math.sin(rad) * r
    x0, y0 = pt(a0)
    x1, y1 = pt(a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'<path d="M{x0:.1f},{y0:.1f} A{r},{r} 0 {large} 1 {x1:.1f},{y1:.1f}" fill="none" '
            f'stroke="{colour}" stroke-width="{sw}" stroke-linecap="round"/>')


def write(name, body):
    (OUT / name).write_text(body + '</svg>\n')
    print(f'  {name:16s} {len(body):6d} B')


# =====================================================================
# HEADER
# =====================================================================
def header():
    W, H = 1200, 300
    s = [head(W, H, 'RelativelyUnknown — I build tools that sit close to the code'),
         box(0, 0, W, H, BG)]

    s.append(txt(64, 132, 'RELATIVELY', size=66, family=SANS, weight='700', ls=-2))
    s.append(txt(64, 202, 'UNKNOWN', size=66, family=SANS, weight='700', ls=-2, op=0.42))

    s.append(txt(660, 116, 'I build tools that sit', size=21, family=SANS, weight='500'))
    s.append(txt(660, 146, 'close to the code.', size=21, family=SANS, weight='500'))
    s.append(txt(660, 186, 'STATIC ANALYSIS  ·  LANGUAGE GRAMMARS  ·  EDITOR TOOLING',
                 size=10, ls=1.4, op=0.5))

    # signature bar — the shape-sequence strip, reduced to pure colour
    seg = [(GREEN, 186), (YELLOW, 98), (VERM, 254), (BLUE, 142), (PINK, 78)]
    x = 64
    for colour, w in seg:
        s.append(box(x, 242, w, 14, colour, rx=7))
        x += w + 12
    return ''.join(s)


# =====================================================================
# PROJECT CARDS — flat colour panel, one mark, caption beneath
# =====================================================================
def card(num, title, line, meta, hue, mark):
    W, H = 380, 404
    s = [head(W, H, f'{title} — {line}'), box(0, 0, W, H, BG)]
    s.append(box(0, 0, W, 236, hue, rx=10))
    s.append(f'<g transform="translate({W/2},118)">{mark}</g>')
    s.append(txt(7, 286, num, size=13, fill=hue, ls=1.6))
    s.append(txt(7, 322, title, size=29, family=SANS, weight='700', ls=-0.6))
    s.append(txt(7, 352, line, size=15, family=SANS, weight='400', op=0.62))
    s.append(txt(7, 386, meta, size=10.5, fill=hue, ls=1.5))
    return ''.join(s)


def mark_meter():
    """Spend rising past a fixed cap."""
    g = []
    for i, h in enumerate((46, 74, 104)):
        g.append(capsule(-96 + i * 62, 62 - h, 40, h, CREAM))
    g.append(capsule(34, 62 - 150, 40, 150, CREAM))
    g.append(stroke_line(-124, -46, 102, -46, BG, 8))
    g.append(dot(54, -46, 11, BG))
    return ''.join(g)


def mark_graph():
    """Three nodes, two links, one flagged."""
    g = [stroke_line(-96, 34, 0, -44, CREAM, 11),
         stroke_line(0, -44, 96, 34, CREAM, 11),
         dot(-96, 34, 27, CREAM),
         dot(0, -44, 27, CREAM)]
    g.append(dot(96, 34, 30, BG))
    g.append(ring(96, 34, 24, CREAM, 12))
    return ''.join(g)


def mark_fan():
    """One root branching into many."""
    g = []
    for dy in (-72, -24, 24, 72):
        g.append(stroke_line(-88, 0, 74, dy, CREAM, 10))
    g.append(dot(-88, 0, 28, CREAM))
    for dy in (-72, -24, 24, 72):
        g.append(dot(84, dy, 16, CREAM))
    return ''.join(g)


# =====================================================================
# STACK — tile grid; colour marks daily use, outline marks occasional
# =====================================================================
def stack():
    cols, tw, th, gap = 6, 182, 58, 12
    LANG, ML, PLAT, INFRA = BLUE, GREEN, VERM, YELLOW
    # exactly six per category, so each row of the grid is one category
    tools = [
        ('Python', LANG, 1), ('Rust', LANG, 1), ('TypeScript', LANG, 1),
        ('SQL', LANG, 1), ('Go', LANG, 0), ('C', LANG, 0),

        ('PyTorch', ML, 1), ('pandas', ML, 1), ('NumPy', ML, 0),
        ('scikit-learn', ML, 0), ('TensorFlow', ML, 0), ('Seaborn', ML, 0),

        ('tree-sitter', PLAT, 1), ('Spark', PLAT, 1), ('Databricks', PLAT, 1),
        ('Postgres', PLAT, 1), ('MySQL', PLAT, 0), ('Grafana', PLAT, 0),

        ('Git', INFRA, 1), ('Linux', INFRA, 1), ('Docker', INFRA, 1),
        ('GitHub Actions', INFRA, 1), ('Kubernetes', INFRA, 0), ('Jenkins', INFRA, 0),
    ]
    rows_n = math.ceil(len(tools) / cols)
    W = cols * tw + (cols - 1) * gap + 128
    H = rows_n * th + (rows_n - 1) * gap + 178
    s = [head(W, H, 'The stack — filled tiles are daily, outlined tiles occasional'), box(0, 0, W, H, BG)]

    s.append(txt(64, 68, 'THE STACK', size=13, ls=3.4))
    s.append(txt(W - 64, 68, f'{len(tools)}', size=13, ls=1.4, op=0.45, anchor='end'))

    for i, (name, hue, daily) in enumerate(tools):
        x = 64 + (i % cols) * (tw + gap)
        y = 104 + (i // cols) * (th + gap)
        if daily:
            s.append(box(x, y, tw, th, hue, rx=8))
            s.append(txt(x + tw / 2, y + th / 2 + 5, name, size=14.5, fill=BG,
                         family=SANS, weight='700', anchor='middle'))
        else:
            s.append(box(x, y, tw, th, 'none', rx=8, stroke=hue, sw=1.5, op=0.6))
            s.append(txt(x + tw / 2, y + th / 2 + 5, name, size=14.5, fill=CREAM,
                         family=SANS, weight='500', anchor='middle', op=0.72))

    ky = H - 40
    s.append(box(64, ky - 11, 26, 14, CREAM, rx=7))
    s.append(txt(100, ky, 'DAILY', size=10, ls=1.4, op=0.55))
    s.append(box(176, ky - 11, 26, 14, 'none', rx=7, stroke=CREAM, sw=1.5, op=0.4))
    s.append(txt(212, ky, 'OCCASIONAL', size=10, ls=1.4, op=0.55))
    for i, (lbl, hue) in enumerate((('LANGUAGE', BLUE), ('MODELLING', GREEN),
                                    ('PLATFORM', VERM), ('INFRASTRUCTURE', YELLOW))):
        bx = 430 + i * 190
        s.append(box(bx, ky - 11, 14, 14, hue, rx=7))
        s.append(txt(bx + 24, ky, lbl, size=10, ls=1.4, op=0.55))
    return ''.join(s)


# =====================================================================
# FOOTER
# =====================================================================
def footer():
    W, H = 1200, 152
    s = [head(W, H, 'Contact — linkedin.com/in/jurreandenys'), box(0, 0, W, H, BG)]
    seg = [(PINK, 78), (BLUE, 142), (VERM, 254), (YELLOW, 98), (GREEN, 186)]
    x = 64
    for colour, w in seg:
        s.append(box(x, 44, w, 14, colour, rx=7))
        x += w + 12
    s.append(txt(64, 112, 'linkedin.com/in/jurreandenys', size=20, family=SANS, weight='500'))
    s.append(txt(W - 64, 112, 'OPEN TO TALK', size=11, fill=GREEN, ls=2, anchor='end'))
    return ''.join(s)


if __name__ == '__main__':
    print('generating:')
    write('head.svg', header())
    write('card-01.svg', card('01', 'Mallard', 'Watches what AI coding costs you.',
                              'TYPESCRIPT · VS CODE', BLUE, mark_meter()))
    write('card-02.svg', card('02', 'burnt', 'Reads a data pipeline as one graph.',
                              'RUST + PYTHON · 110 RULES', GREEN, mark_graph()))
    write('card-03.svg', card('03', 'tree-sitter-sql', 'One grammar, twenty-two dialects.',
                              'RUST + C · NODE / PY / GO', VERM, mark_fan()))
    write('stack.svg', stack())
    write('foot.svg', footer())
    print('done')

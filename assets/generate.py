#!/usr/bin/env python3
"""SVG plates for the RelativelyUnknown profile README.

Design language taken from the reference board, whose dominant device is the
SPECIMEN PLATE: a grid of variations on one theme, each drawn as a hairline
ink mark and captioned in small tracked capitals (network-topology plate,
serve-decomposition grid, signal-glyph grid, Bauhaus cell grid, logo
explorations). Supporting devices: warm paper ground with a faint dot grid,
bead/dot columns encoding data, graded legend strips, registration marks,
tick rulers and an engineering title block.
"""
import math
import pathlib

OUT = pathlib.Path(__file__).resolve().parent

# ---- palette (sampled from the board: 57, 66, 131, 119, 165, 72, 162) ----
PAPER   = '#EFE8D8'
PLATE   = '#F6F2E7'
INK     = '#16181D'
SOFT    = '#8C8676'
FAINT   = '#BDB6A3'
RULE    = '#CFC7B4'
VERM    = '#DF3B22'
MUSTARD = '#EFA820'
GREEN   = '#2E8B4E'
COBALT  = '#2F5DA8'
INDIGO  = '#5B5FA8'
CORAL   = '#EE8873'
TEAL    = '#159A8C'

MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,'DejaVu Sans Mono',monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def head(w, h, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" '
            f'height="{h}" role="img" aria-label="{esc(label)}">')


def txt(x, y, s, size=10, fill=INK, family=MONO, weight='400', anchor='start', ls=0, op=None):
    o = f' opacity="{op}"' if op is not None else ''
    l = f' letter-spacing="{ls}"' if ls else ''
    return (f'<text x="{x}" y="{y}" font-family="{family}" font-size="{size}" font-weight="{weight}" '
            f'fill="{fill}" text-anchor="{anchor}"{l}{o}>{esc(s)}</text>')


def rect(x, y, w, h, fill='none', stroke=None, sw=1, rx=0, dash=None, op=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' opacity="{op}"' if op is not None else ''
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}"{s}{d}{o}/>'


def line(x1, y1, x2, y2, stroke=RULE, sw=1, dash=None, op=None, cap=None):
    d = f' stroke-dasharray="{dash}"' if dash else ''
    o = f' opacity="{op}"' if op is not None else ''
    c = f' stroke-linecap="{cap}"' if cap else ''
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}"{d}{o}{c}/>'


def circ(cx, cy, r, fill='none', stroke=None, sw=1, op=None, dash=None):
    s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
    o = f' opacity="{op}"' if op is not None else ''
    d = f' stroke-dasharray="{dash}"' if dash else ''
    return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}"{s}{d}{o}/>'


def path(d, fill='none', stroke=INK, sw=1, op=None, cap='round', join='round', dash=None):
    o = f' opacity="{op}"' if op is not None else ''
    da = f' stroke-dasharray="{dash}"' if dash else ''
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}" stroke-linejoin="{join}"{o}{da}/>')


def dotgrid(x, y, w, h, step=22, r=1, fill=FAINT, op=0.55):
    """The faint pinned-paper dot grid (ref 66)."""
    p = [f'<g fill="{fill}" opacity="{op}">']
    for gy in range(int(y), int(y + h), step):
        for gx in range(int(x), int(x + w), step):
            p.append(f'<circle cx="{gx}" cy="{gy}" r="{r}"/>')
    p.append('</g>')
    return ''.join(p)


def reg(x, y, w, h, s=6, fill=INK, op=0.75):
    """Corner registration squares (ref 123, 139)."""
    o = []
    for cx, cy in ((x, y), (x + w - s, y), (x, y + h - s), (x + w - s, y + h - s)):
        o.append(f'<rect x="{cx}" y="{cy}" width="{s}" height="{s}" fill="{fill}" opacity="{op}"/>')
    return ''.join(o)


def ruler(x, y, w, step=10, major=5, minor_h=3, major_h=7, stroke=FAINT,
          label_every=0, scale=1, size=7):
    p = []
    for i in range(int(w // step) + 1):
        cx = x + i * step
        hh = major_h if i % major == 0 else minor_h
        p.append(line(cx, y, cx, y + hh, stroke, 1))
        if label_every and i % label_every == 0:
            p.append(txt(cx, y + hh + 9, str(int(i * scale)), size=size, fill=SOFT, anchor='middle'))
    return ''.join(p)


def caption(cx, y, name, sub=None):
    """Specimen caption: tracked caps, optional second line (ref 162)."""
    o = [txt(cx, y, name, size=8.5, fill=INK, anchor='middle', ls=1.7)]
    if sub:
        o.append(txt(cx, y + 12, sub, size=7.5, fill=SOFT, anchor='middle', ls=1.2))
    return ''.join(o)


def beads(x, y, items, r=5.5, gap=15):
    """Lupi-style bead run: filled dot + inner dot (ref 131, 66)."""
    o = []
    for i, (col, solid) in enumerate(items):
        cx = x + i * gap
        if solid:
            o.append(circ(cx, y, r, fill=col))
            o.append(circ(cx, y, r * 0.34, fill=PLATE))
        else:
            o.append(circ(cx, y, r, fill='none', stroke=col, sw=1.4))
    return ''.join(o)


def write(name, body):
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(body + '</svg>\n')
    print(f'  {name:22s} {len(body):6d} B')


# =====================================================================
# HEADER PLATE
# =====================================================================
def plate():
    W, H = 1200, 340
    s = [head(W, H, 'RelativelyUnknown — plate one'), rect(0, 0, W, H, PAPER)]
    s.append(rect(16, 16, W - 32, H - 32, PLATE, RULE, 1))
    s.append(dotgrid(40, 40, W - 80, H - 80))
    s.append(reg(28, 28, W - 56, H - 56))

    s.append(txt(46, 56, 'PLATE  I', size=9, fill=SOFT, ls=2.4))
    s.append(txt(W - 46, 56, 'RU / 2026 / 01', size=9, fill=SOFT, ls=1.6, anchor='end'))
    s.append(line(46, 68, W - 46, 68, RULE))

    s.append(txt(46, 150, 'RELATIVELY', size=64, fill=INK, family=SANS, weight='700', ls=-1.4))
    s.append(txt(46, 214, 'UNKNOWN', size=64, fill='none', family=SANS, weight='700', ls=-1.4)
             .replace('fill="none"', f'fill="{PLATE}" stroke="{INK}" stroke-width="1.4"'))

    # strapline block
    s.append(rect(474, 118, 3, 96, VERM))
    for i, ln in enumerate([
            'I BUILD TOOLS THAT SIT CLOSE TO THE CODE:',
            'STATIC ANALYSIS, LANGUAGE GRAMMARS,',
            'AND THE EDITOR SURFACES AROUND THEM.']):
        s.append(txt(492, 136 + i * 19, ln, size=11.5, fill=INK, ls=1.5))
    s.append(txt(492, 200, 'DATA + AI ENGINEERING', size=9, fill=SOFT, ls=2.2))

    # legend strip: graded swatches (ref 119)
    lx, ly = 880, 118
    s.append(txt(lx, ly - 6, 'DENSITY OF USE', size=8, fill=SOFT, ls=1.6))
    for i in range(6):
        op = 0.16 + i * 0.168
        s.append(rect(lx + i * 26, ly + 4, 20, 20, INK, op=round(op, 2)))
    s.append(txt(lx, ly + 40, 'OCCASIONAL', size=7, fill=SOFT, ls=1))
    s.append(txt(lx + 156, ly + 40, 'DAILY', size=7, fill=SOFT, ls=1, anchor='end'))

    # bead row (ref 131) — the three live projects
    s.append(txt(lx, ly + 74, 'ACTIVE SPECIMENS', size=8, fill=SOFT, ls=1.6))
    s.append(beads(lx + 7, ly + 92, [(COBALT, True), (GREEN, True), (VERM, True)], r=7, gap=22))
    s.append(txt(lx + 74, ly + 96, '03', size=13, fill=INK))

    # tick scale + footer line
    s.append(ruler(46, 262, 700, step=11, major=5, label_every=10, scale=10))
    s.append(line(46, 300, W - 46, 300, RULE))
    s.append(txt(46, 318, 'DRAWN FROM LIFE — EVERY MARK ON THIS PLATE ENCODES SOMETHING REAL',
                 size=8.5, fill=SOFT, ls=1.6))
    s.append(txt(W - 46, 318, 'SHEET 1 OF 3', size=8.5, fill=SOFT, ls=1.6, anchor='end'))
    return ''.join(s)


# =====================================================================
# PROJECT SPECIMENS
# =====================================================================
def specimen(num, name, taxon, lines, rows, bead_items, drawing, accent):
    """Full-width specimen strip: drawing left, identification centre, data right."""
    W, H = 1200, 248
    s = [head(W, H, f'{name} — {taxon}'), rect(0, 0, W, H, PAPER)]
    s.append(rect(12, 12, W - 24, H - 24, PLATE, RULE, 1))
    s.append(dotgrid(30, 30, W - 60, H - 60, step=22, op=0.42))
    s.append(reg(22, 22, W - 44, H - 44, s=5))

    s.append(txt(38, 40, f'SPEC. {num}', size=8.5, fill=SOFT, ls=2))
    s.append(line(38, 50, W - 38, 50, RULE))

    # drawing well, scaled down from the 388-wide original
    s.append(f'<g transform="translate(34,62) scale(0.80)">{drawing}</g>')
    s.append(line(360, 66, 360, H - 40, FAINT, 1, op=0.6))

    # identification
    s.append(caption(600, 106, taxon))
    s.append(txt(600, 150, name, size=30, fill=INK, family=SANS, weight='700',
                 anchor='middle', ls=-0.4))
    for i, ln in enumerate(lines):
        s.append(txt(600, 178 + i * 17, ln, size=11, fill=SOFT, anchor='middle'))
    s.append(beads(600 - (len(bead_items) - 1) * 9, 218, bead_items, r=5.5, gap=18))
    s.append(line(840, 66, 840, H - 40, FAINT, 1, op=0.6))

    # data block
    s.append(circ(W - 44, 40, 5.5, fill=accent))
    y0 = 96
    for i, (k, v) in enumerate(rows):
        y = y0 + i * 26
        s.append(txt(866, y, k, size=9.5, fill=SOFT, ls=0.8))
        s.append(txt(W - 38, y, v, size=11, fill=INK, anchor='end'))
        s.append(line(866, y + 6, W - 38, y + 6, FAINT, dash='1 4', op=0.75))
    s.append(txt(866, H - 26, 'github.com/RelativelyUnknown', size=8.5, fill=FAINT, ls=0.6))
    return ''.join(s)


def strip(label, title, sheet):
    """Thin plate-divider rule (used to open the specimen section)."""
    W, H = 1200, 62
    s = [head(W, H, title), rect(0, 0, W, H, PAPER)]
    s.append(line(38, 30, W - 38, 30, RULE))
    s.append(rect(38, 22, 3, 16, VERM))
    s.append(txt(54, 35, label, size=9, fill=SOFT, ls=2.4))
    s.append(txt(W / 2, 35, title, size=12, fill=INK, anchor='middle', ls=3.2))
    s.append(txt(W - 38, 35, sheet, size=9, fill=SOFT, ls=1.6, anchor='end'))
    return ''.join(s)


def draw_burst():
    """Centralized burst — spend radiating from one hub, one ray over the cap."""
    cx, cy, g = 194, 100, []
    g.append(circ(cx, cy, 78, stroke=FAINT, sw=1, dash='2 5'))
    g.append(circ(cx, cy, 54, stroke=FAINT, sw=1, dash='2 5'))
    n = 26
    for i in range(n):
        a = (i / n) * math.tau - math.pi / 2
        over = i in (3, 11, 19)
        rr = 92 if over else 30 + (i * 37 % 46)
        x, y = cx + math.cos(a) * rr, cy + math.sin(a) * rr
        col = VERM if over else INK
        g.append(line(cx, cy, x, y, col, 1.1 if over else 0.9, op=1 if over else 0.55))
        g.append(circ(x, y, 3.4 if over else 2.4, fill=col, op=1 if over else 0.6))
    g.append(circ(cx, cy, 12, fill=COBALT))
    g.append(circ(cx, cy, 4.2, fill=PLATE))
    g.append(txt(cx + 86, cy - 62, 'over cap', size=7.5, fill=VERM, ls=0.6))
    return ''.join(g)


def draw_rhizome():
    """Organic rhizome — a code graph, three nodes flagged."""
    g = []
    pts = [(60, 100), (104, 66), (104, 134), (150, 44), (150, 100), (150, 156),
           (200, 30), (200, 78), (200, 122), (200, 170), (250, 56), (250, 100),
           (250, 144), (298, 78), (298, 122), (334, 100)]
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (2, 5), (3, 6), (4, 7), (4, 8),
             (5, 9), (6, 10), (7, 10), (8, 11), (8, 12), (9, 12), (10, 13), (11, 13),
             (11, 14), (12, 14), (13, 15), (14, 15)]
    flagged = {7, 11, 14}
    for a, b in edges:
        x1, y1 = pts[a]
        x2, y2 = pts[b]
        mx = (x1 + x2) / 2
        g.append(path(f'M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}', stroke=INK, sw=0.9, op=0.5))
    for i, (x, y) in enumerate(pts):
        if i in flagged:
            g.append(circ(x, y, 10, stroke=VERM, sw=1, op=0.5))
            g.append(circ(x, y, 4.6, fill=VERM))
        else:
            g.append(circ(x, y, 3.6, fill=PLATE, stroke=INK, sw=1.2))
    g.append(circ(60, 100, 6, fill=GREEN))
    return ''.join(g)


def draw_ramification():
    """Ramification — one grammar branching into dialects."""
    g = []
    root = (40, 100)
    t1 = [(112, 58), (112, 100), (112, 142)]
    t2 = [(192, 34), (192, 66), (192, 92), (192, 112), (192, 138), (192, 168)]
    leaves = [(288, 18 + i * 15.6) for i in range(11)]
    for t in t1:
        g.append(path(f'M{root[0]},{root[1]} C{(root[0]+t[0])/2},{root[1]} '
                      f'{(root[0]+t[0])/2},{t[1]} {t[0]},{t[1]}', stroke=INK, sw=1.2, op=0.8))
    link2 = [(0, 0), (0, 1), (1, 2), (1, 3), (2, 4), (2, 5)]
    for a, b in link2:
        x1, y1 = t1[a]
        x2, y2 = t2[b]
        g.append(path(f'M{x1},{y1} C{(x1+x2)/2},{y1} {(x1+x2)/2},{y2} {x2},{y2}',
                      stroke=INK, sw=1, op=0.6))
    for i, (lx, ly) in enumerate(leaves):
        sx, sy = t2[min(int(i * len(t2) / len(leaves)), len(t2) - 1)]
        g.append(path(f'M{sx},{sy} C{(sx+lx)/2},{sy} {(sx+lx)/2},{ly} {lx},{ly}',
                      stroke=INK, sw=0.8, op=0.42))
    g.append(circ(*root, 8, fill=VERM))
    g.append(circ(root[0], root[1], 2.8, fill=PLATE))
    for x, y in t1:
        g.append(circ(x, y, 4.4, fill=PLATE, stroke=INK, sw=1.2))
    for x, y in t2:
        g.append(circ(x, y, 3.2, fill=INK, op=0.7))
    for i, (x, y) in enumerate(leaves):
        c = MUSTARD if i % 3 == 0 else INK
        g.append(rect(x - 2.6, y - 2.6, 5.2, 5.2, c, op=1 if c == MUSTARD else 0.65))
    return ''.join(g)


# =====================================================================
# TAXONOMY PLATE — the tooling, drawn as specimens
# =====================================================================
def taxonomy():
    cols, cw, ch = 6, 194, 158
    items = [
        ('PYTHON', 'daily', 'rhizome', GREEN),
        ('RUST', 'daily', 'lattice', VERM),
        ('TYPESCRIPT', 'daily', 'arc', COBALT),
        ('GO', 'bindings', 'ties', TEAL),
        ('C', 'bindings', 'grid', INK),
        ('SQL', 'daily', 'ramify', MUSTARD),
        ('TREE-SITTER', 'parsing', 'tree', GREEN),
        ('SPARK', 'engine', 'converge', VERM),
        ('DATABRICKS', 'platform', 'strata', CORAL),
        ('POSTGRES', 'store', 'rings', COBALT),
        ('MYSQL', 'store', 'spiral', INDIGO),
        ('PANDAS', 'data', 'columns', MUSTARD),
        ('NUMPY', 'data', 'matrix', COBALT),
        ('SCIKIT-LEARN', 'models', 'cluster', MUSTARD),
        ('PYTORCH', 'models', 'gradient', VERM),
        ('TENSORFLOW', 'models', 'flow', MUSTARD),
        ('SEABORN', 'plots', 'dist', TEAL),
        ('DOCKER', 'infra', 'stack', COBALT),
        ('KUBERNETES', 'infra', 'cells', INDIGO),
        ('LINUX', 'infra', 'burst', INK),
        ('GIT', 'infra', 'braid', VERM),
        ('GITHUB ACTIONS', 'ci', 'chain', GREEN),
        ('JENKINS', 'ci', 'relay', SOFT),
        ('GRAFANA', 'observe', 'trace', MUSTARD),
    ]
    rows_n = math.ceil(len(items) / cols)
    W = cols * cw + 40
    H = rows_n * ch + 116
    s = [head(W, H, 'Taxonomy of tooling'), rect(0, 0, W, H, PAPER)]
    s.append(rect(14, 14, W - 28, H - 28, PLATE, RULE, 1))
    s.append(dotgrid(34, 34, W - 68, H - 68, step=24, op=0.38))
    s.append(reg(24, 24, W - 48, H - 48))

    s.append(txt(44, 52, 'PLATE  III', size=9, fill=SOFT, ls=2.4))
    s.append(txt(W / 2, 52, 'A TAXONOMY OF TOOLING', size=13, fill=INK, anchor='middle', ls=3.4))
    s.append(txt(W - 44, 52, f'{len(items)} SPECIMENS', size=9, fill=SOFT, ls=1.6, anchor='end'))
    s.append(line(44, 64, W - 44, 64, RULE))

    def glyph(kind, cx, cy, col):
        g = []
        if kind == 'rhizome':
            pts = [(0, 0), (-26, -14), (26, -12), (-16, 16), (18, 18), (-40, 6), (40, 2), (4, -30)]
            for i in range(1, len(pts)):
                g.append(line(cx + pts[0][0], cy + pts[0][1], cx + pts[i][0], cy + pts[i][1], INK, 0.9, op=0.55))
            for i in (1, 2, 3, 4):
                for j in (5, 6, 7):
                    if (i + j) % 3 == 0:
                        g.append(line(cx + pts[i][0], cy + pts[i][1], cx + pts[j][0], cy + pts[j][1], INK, 0.8, op=0.35))
            for i, (dx, dy) in enumerate(pts):
                g.append(circ(cx + dx, cy + dy, 5 if i == 0 else 3.2, fill=col if i == 0 else INK,
                              op=None if i == 0 else 0.75))
        elif kind == 'lattice':
            for i in range(4):
                for j in range(4):
                    x, y = cx - 27 + j * 18, cy - 27 + i * 18
                    g.append(rect(x, y, 12, 12, col if (i + j) % 3 == 0 else 'none',
                                  None if (i + j) % 3 == 0 else INK, 0.9,
                                  op=1 if (i + j) % 3 == 0 else 0.5))
        elif kind == 'arc':
            for i, r in enumerate((14, 22, 30, 38)):
                g.append(path(f'M{cx-r},{cy+16} A{r},{r} 0 0 1 {cx+r},{cy+16}', stroke=col if i % 2 == 0 else INK,
                              sw=1.2, op=1 if i % 2 == 0 else 0.45))
            g.append(line(cx - 42, cy + 16, cx + 42, cy + 16, INK, 1, op=0.6))
            for dx in (-38, -22, 0, 22, 38):
                g.append(circ(cx + dx, cy + 16, 2.6, fill=INK, op=0.8))
        elif kind == 'ties':
            g.append(circ(cx, cy, 30, stroke=INK, sw=0.9, op=0.4))
            n = 9
            ps = [(cx + math.cos(i / n * math.tau) * 30, cy + math.sin(i / n * math.tau) * 30) for i in range(n)]
            for i in range(n):
                g.append(path(f'M{ps[i][0]:.1f},{ps[i][1]:.1f} Q{cx},{cy} '
                              f'{ps[(i*4) % n][0]:.1f},{ps[(i*4) % n][1]:.1f}', stroke=INK, sw=0.8, op=0.45))
            for i, (x, y) in enumerate(ps):
                g.append(circ(x, y, 3.2, fill=col if i % 3 == 0 else INK, op=None if i % 3 == 0 else 0.7))
        elif kind == 'grid':
            for i in range(5):
                g.append(line(cx - 32 + i * 16, cy - 30, cx - 32 + i * 16, cy + 30, INK, 0.9, op=0.55))
                g.append(line(cx - 32, cy - 30 + i * 15, cx + 32, cy - 30 + i * 15, INK, 0.9, op=0.55))
            g.append(rect(cx - 16, cy - 15, 16, 15, col, op=0.9))
        elif kind == 'ramify':
            g.append(path(f'M{cx-38},{cy} L{cx-14},{cy}', stroke=INK, sw=1.2))
            for i, dy in enumerate((-24, -8, 8, 24)):
                g.append(path(f'M{cx-14},{cy} C{cx},{cy} {cx},{cy+dy} {cx+18},{cy+dy}', stroke=INK, sw=1, op=0.65))
                g.append(circ(cx + 20, cy + dy, 3, fill=col if i % 2 == 0 else INK, op=None if i % 2 == 0 else 0.7))
            g.append(circ(cx - 38, cy, 4.4, fill=col))
        elif kind == 'tree':
            g.append(path(f'M{cx},{cy-30} L{cx-24},{cy-2} M{cx},{cy-30} L{cx+24},{cy-2} '
                          f'M{cx-24},{cy-2} L{cx-34},{cy+26} M{cx-24},{cy-2} L{cx-12},{cy+26} '
                          f'M{cx+24},{cy-2} L{cx+14},{cy+26} M{cx+24},{cy-2} L{cx+34},{cy+26}',
                          stroke=INK, sw=1, op=0.75))
            g.append(circ(cx, cy - 30, 5, fill=col))
            for dx in (-24, 24):
                g.append(circ(cx + dx, cy - 2, 3.4, fill=PLATE, stroke=INK, sw=1.1))
            for dx in (-34, -12, 14, 34):
                g.append(rect(cx + dx - 2.6, cy + 24, 5.2, 5.2, INK, op=0.7))
        elif kind == 'converge':
            for i, dy in enumerate((-28, -14, 0, 14, 28)):
                g.append(path(f'M{cx-38},{cy+dy} C{cx-10},{cy+dy} {cx-4},{cy} {cx+26},{cy}',
                              stroke=col if i == 2 else INK, sw=1.1, op=1 if i == 2 else 0.45))
                g.append(circ(cx - 38, cy + dy, 2.8, fill=INK, op=0.7))
            g.append(circ(cx + 28, cy, 5.5, fill=col))
        elif kind == 'strata':
            for i, o in enumerate((0.3, 0.5, 0.72, 1)):
                g.append(path(f'M{cx},{cy-26+i*15} l30,11 l-30,11 l-30,-11 z', stroke=col, sw=1.1, op=o))
        elif kind == 'rings':
            for i, r in enumerate((10, 19, 28)):
                g.append(circ(cx, cy, r, stroke=col if i == 1 else INK, sw=1.2, op=1 if i == 1 else 0.5))
            g.append(circ(cx, cy, 4, fill=INK))
            for a in range(0, 360, 45):
                rad = math.radians(a)
                g.append(circ(cx + math.cos(rad) * 28, cy + math.sin(rad) * 28, 2.2, fill=INK, op=0.6))
        elif kind == 'columns':
            for i, v in enumerate((18, 34, 24, 44, 30, 38)):
                x = cx - 34 + i * 13
                g.append(rect(x, cy + 24 - v, 8, v, col if i in (1, 3) else INK,
                              op=1 if i in (1, 3) else 0.45))
            g.append(line(cx - 38, cy + 24, cx + 38, cy + 24, INK, 1, op=0.7))
        elif kind == 'matrix':
            for i in range(4):
                for j in range(5):
                    v = (i * 5 + j * 3) % 7
                    g.append(rect(cx - 34 + j * 15, cy - 24 + i * 13, 11, 9, INK, op=round(0.15 + v * 0.11, 2)))
            g.append(rect(cx - 34 + 30, cy - 24 + 13, 11, 9, col))
        elif kind == 'cluster':
            groups = [((-22, -12), 5), ((18, -16), 4), ((6, 18), 6)]
            cols_ = [col, INK, INK]
            for gi, ((gx, gy), n) in enumerate(groups):
                for k in range(n):
                    a = k / n * math.tau
                    rr = 9 + (k % 3) * 4
                    g.append(circ(cx + gx + math.cos(a) * rr, cy + gy + math.sin(a) * rr, 3,
                                  fill=cols_[gi], op=1 if gi == 0 else 0.6))
                g.append(circ(cx + gx, cy + gy, 17, stroke=INK, sw=0.8, op=0.3, fill='none'))
        elif kind == 'gradient':
            g.append(path(f'M{cx-34},{cy+24} C{cx-14},{cy+24} {cx-10},{cy-24} {cx+8},{cy-24} '
                          f'S{cx+22},{cy+6} {cx+34},{cy+4}', stroke=col, sw=1.4))
            for i, dx in enumerate((-24, -10, 4, 18, 30)):
                yy = cy + 22 - i * 10
                g.append(circ(cx + dx, yy, 2.8, fill=INK, op=0.75))
                g.append(line(cx + dx - 7, yy + 4, cx + dx + 7, yy - 4, INK, 0.9, op=0.45))
        elif kind == 'flow':
            for i, dy in enumerate((-20, 0, 20)):
                g.append(path(f'M{cx-36},{cy+dy} C{cx-6},{cy+dy} {cx-6},{cy-dy} {cx+36},{cy-dy}',
                              stroke=col if i == 1 else INK, sw=1.3, op=1 if i == 1 else 0.5))
            for dy in (-20, 0, 20):
                g.append(circ(cx - 36, cy + dy, 2.8, fill=INK, op=0.7))
                g.append(circ(cx + 36, cy + dy, 2.8, fill=INK, op=0.7))
        elif kind == 'dist':
            g.append(path(f'M{cx-36},{cy+24} C{cx-16},{cy+24} {cx-14},{cy-24} {cx},{cy-24} '
                          f'S{cx+16},{cy+24} {cx+36},{cy+24}', stroke=col, sw=1.3))
            g.append(line(cx, cy - 24, cx, cy + 24, INK, 0.9, dash='2 3', op=0.55))
            for dx in (-18, 0, 18):
                g.append(circ(cx + dx, cy + 24, 2.6, fill=INK, op=0.7))
        elif kind == 'stack':
            for i, o in enumerate((0.35, 0.6, 1)):
                y = cy - 20 + i * 16
                g.append(rect(cx - 30, y, 60, 12, 'none', col, 1.2, op=o))
                g.append(circ(cx - 22, y + 6, 2.2, fill=col, op=o))
        elif kind == 'cells':
            for i, (dx, dy) in enumerate(((0, -22), (-20, -10), (20, -10), (-20, 12), (20, 12), (0, 24))):
                g.append(path(f'M{cx+dx},{cy+dy-11} l10,5.5 l0,11 l-10,5.5 l-10,-5.5 l0,-11 z',
                              stroke=INK, sw=1, op=0.6))
            g.append(path(f'M{cx},{cy+1-11} l10,5.5 l0,11 l-10,5.5 l-10,-5.5 l0,-11 z', stroke=col, sw=1.4))
        elif kind == 'burst':
            for i in range(16):
                a = i / 16 * math.tau
                rr = 16 + (i * 11 % 20)
                g.append(line(cx, cy, cx + math.cos(a) * rr, cy + math.sin(a) * rr, INK, 0.9, op=0.55))
                g.append(circ(cx + math.cos(a) * rr, cy + math.sin(a) * rr, 2.2, fill=INK, op=0.7))
            g.append(circ(cx, cy, 6, fill=col))
        elif kind == 'braid':
            g.append(path(f'M{cx-34},{cy-16} L{cx-34},{cy+22}', stroke=INK, sw=1.3, op=0.8))
            g.append(path(f'M{cx-34},{cy-2} C{cx-16},{cy-2} {cx-12},{cy-18} {cx+6},{cy-18} L{cx+22},{cy-18}',
                          stroke=col, sw=1.3))
            g.append(path(f'M{cx-34},{cy+10} C{cx-14},{cy+10} {cx-8},{cy+22} {cx+22},{cy+22}',
                          stroke=INK, sw=1.2, op=0.55))
            for px, py, c in ((cx - 34, cy - 16, INK), (cx - 34, cy + 22, INK),
                              (cx + 22, cy - 18, col), (cx + 22, cy + 22, INK)):
                g.append(circ(px, py, 3.6, fill=PLATE, stroke=c, sw=1.4))
        elif kind == 'chain':
            for i in range(4):
                x = cx - 30 + i * 20
                g.append(rect(x - 6, cy - 7, 13, 14, 'none', col if i == 3 else INK, 1.1,
                              op=1 if i == 3 else 0.55, rx=2))
                if i < 3:
                    g.append(line(x + 7, cy, x + 14, cy, INK, 1, op=0.5))
            g.append(path(f'M{cx+26},{cy-14} l7,7 l-7,7', stroke=col, sw=1.3))
        elif kind == 'spiral':
            d = 'M'
            for i in range(64):
                t = i / 63
                a = t * math.tau * 2.1
                rr = 4 + t * 28
                d += f'{cx + math.cos(a) * rr:.1f},{cy + math.sin(a) * rr:.1f} '
                if i == 0:
                    d += 'L'
            g.append(path(d.strip(), stroke=col, sw=1.2))
            for i in (12, 30, 48, 62):
                t = i / 63
                a = t * math.tau * 2.1
                rr = 4 + t * 28
                g.append(circ(cx + math.cos(a) * rr, cy + math.sin(a) * rr, 2.8, fill=INK, op=0.72))
            g.append(circ(cx, cy, 3.4, fill=col))
        elif kind == 'relay':
            g.append(line(cx - 34, cy - 18, cx + 34, cy - 18, INK, 1, op=0.45))
            g.append(line(cx - 34, cy + 18, cx + 34, cy + 18, INK, 1, op=0.45))
            for i, dx in enumerate((-24, -4, 16)):
                g.append(circ(cx + dx, cy - 18, 3.6, fill=PLATE, stroke=INK, sw=1.2))
                g.append(circ(cx + dx + 12, cy + 18, 3.6, fill=PLATE, stroke=INK, sw=1.2))
                g.append(path(f'M{cx+dx},{cy-18} C{cx+dx+6},{cy-6} {cx+dx+6},{cy+6} {cx+dx+12},{cy+18}',
                              stroke=col if i == 1 else INK, sw=1.2, op=1 if i == 1 else 0.5))
            g.append(circ(cx + 34, cy - 18, 2.4, fill=col))
        elif kind == 'trace':
            pts = [(-36, 10), (-28, -4), (-20, 6), (-12, -14), (-4, 2), (4, -20),
                   (12, -6), (20, -16), (28, 4), (36, -2)]
            d = 'M' + ' L'.join(f'{cx+x},{cy+y}' for x, y in pts)
            g.append(path(d, stroke=col, sw=1.3))
            g.append(line(cx - 38, cy + 22, cx + 38, cy + 22, INK, 1, op=0.6))
            for x, y in pts[::3]:
                g.append(circ(cx + x, cy + y, 2.4, fill=INK, op=0.75))
        return ''.join(g)

    for i, (name, cat, kind, col) in enumerate(items):
        c, r = i % cols, i // cols
        x = 20 + c * cw
        y = 78 + r * ch
        cx, cy = x + cw / 2, y + 56
        s.append(glyph(kind, cx, cy, col))
        s.append(caption(cx, y + 118, name, cat))
        if c < cols - 1:
            s.append(line(x + cw - 2, y + 16, x + cw - 2, y + ch - 22, FAINT, 1, op=0.5))
    s.append(line(44, H - 46, W - 44, H - 46, RULE))
    s.append(txt(44, H - 28, 'MARK DENSITY INDICATES REACH FOR FREQUENCY, NOT PROFICIENCY',
                 size=8.5, fill=SOFT, ls=1.5))
    s.append(txt(W - 44, H - 28, 'PLATE III', size=8.5, fill=SOFT, ls=1.6, anchor='end'))
    return ''.join(s)


# =====================================================================
# COLOPHON — engineering title block (ref 100)
# =====================================================================
def colophon():
    W, H = 1200, 150
    s = [head(W, H, 'Colophon and contact'), rect(0, 0, W, H, PAPER)]
    s.append(rect(14, 14, W - 28, H - 28, PLATE, RULE, 1))
    s.append(reg(24, 24, W - 48, H - 48, s=5))
    ty, th = 44, 62
    cells = [(44, 316, 'CONTACT', 'linkedin.com/in/jurreandenys', COBALT),
             (360, 300, 'INDEX', 'github.com/RelativelyUnknown', INK),
             (660, 200, 'SUBJECTS', 'tooling / analysis / AI', INK),
             (860, 140, 'REV', 'C', VERM),
             (1000, 156, 'STATUS', 'open to talk', GREEN)]
    s.append(line(44, ty, W - 44, ty, INK, 1, op=0.55))
    s.append(line(44, ty + th, W - 44, ty + th, INK, 1, op=0.55))
    for x, w, k, v, col in cells:
        s.append(line(x, ty, x, ty + th, INK, 1, op=0.55))
        s.append(txt(x + 12, ty + 20, k, size=7.5, fill=SOFT, ls=1.6))
        s.append(txt(x + 12, ty + 44, v, size=12.5, fill=col))
    s.append(line(W - 44, ty, W - 44, ty + th, INK, 1, op=0.55))
    s.append(txt(44, 30, 'COLOPHON', size=9, fill=SOFT, ls=2.4))
    s.append(txt(W - 44, 30, 'SHEET 3 OF 3', size=9, fill=SOFT, ls=1.6, anchor='end'))
    s.append(ruler(44, 122, 1112, step=10, major=6))
    return ''.join(s)


if __name__ == '__main__':
    print('generating:')
    write('plate.svg', plate())
    write('spec-01.svg', specimen(
        '01', 'Mallard', 'CENTRALISED BURST',
        ['Every AI coding request bills back', 'to one budget. This watches it.'],
        [('surface', 'VS Code + server'), ('language', 'TypeScript'), ('state', 'published')],
        [(COBALT, True), (COBALT, False), (MUSTARD, True), (INK, False)],
        draw_burst(), COBALT))
    write('spec-02.svg', specimen(
        '02', 'burnt', 'ORGANIC RHIZOME',
        ['Databricks and Spark pipelines,', 'read as one graph and linted.'],
        [('engine', 'Rust + Python'), ('rules', '110'), ('output', 'SARIF')],
        [(GREEN, True), (VERM, True), (GREEN, False), (INK, False)],
        draw_rhizome(), GREEN))
    write('spec-03.svg', specimen(
        '03', 'tree-sitter-sql', 'RAMIFICATION',
        ['One ANSI grammar, branching into', 'twenty-two SQL dialects.'],
        [('language', 'Rust + C'), ('dialects', '22 + ANSI base'), ('bindings', 'node / py / go'), ('base', 'DerekStride fork')],
        [(VERM, True), (MUSTARD, True), (VERM, False), (INK, False)],
        draw_ramification(), VERM))
    write('strip-ii.svg', strip('PLATE  II', 'THREE SPECIMENS, LIVING COLLECTION', 'SHEET 2 OF 3'))
    write('taxonomy.svg', taxonomy())
    write('colophon.svg', colophon())
    print('done')

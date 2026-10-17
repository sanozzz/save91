"""Chart and diagram components for the Slides format (inline styles, pinned hosts,
no empty spacer divs, at most 24 pinned children per host). Each returns an HTML
fragment sized in px. Labels are <p> elements, never SVG <text>.
"""
from __future__ import annotations

import math

import numpy as np
from scipy import stats

from build_deck import BLUE, BODY, CARD, GREY, INK, LBLUE, MUTED, ORANGE, PAPER, SAND

LIGHT = "#DDD6C8"
BROWN = "#8A3B08"


def _p(text, size=24, color=BODY, extra=""):
    return f'<p style="font-size:{size}px;line-height:1.3;color:{color};{extra}">{text}</p>'


def histogram(bins, fmt, width=1664, height=360, zero=0.0, ticks=None, note_pos=None):
    """bins: list of (lo, hi, share). Bars left of `zero` orange, right of it blue."""
    n = len(bins)
    gap = 4
    bw = (width - gap * (n - 1)) / n
    top = max(b[2] for b in bins)
    bars = "".join(
        f'<div style="width:{bw:.1f}px;height:{max(2, b[2] / top * (height - 10)):.0f}px;'
        f'background:{BLUE if (b[0] + b[1]) / 2 >= zero else ORANGE};border-radius:3px 3px 0 0"></div>'
        for b in bins)
    lo, hi = bins[0][0], bins[-1][1]
    xpos = lambda v: (v - lo) / (hi - lo) * width
    pins = []
    if lo < zero < hi:
        pins.append(f'<div style="position:absolute;left:{xpos(zero) - 1:.0f}px;top:0px;width:3px;height:{height}px;background:{INK}"></div>')
    for v in (ticks or []):
        if lo <= v <= hi:
            x = xpos(v)
            pins.append(f'<p style="position:absolute;left:{max(0, min(width - 160, x - 80)):.0f}px;top:{height + 8}px;width:160px;'
                        f'font-size:24px;color:{MUTED};text-align:center">{fmt(v)}</p>')
    return (f'<div style="position:relative;width:{width}px;height:{height + 44}px">'
            f'<div style="display:flex;gap:{gap}px;align-items:flex-end;height:{height}px">{bars}</div>{"".join(pins)}</div>')


def tornado(rows, fmt, label_w=440, track_w=1000, value_w=180):
    """rows: list of (label, low_net, base_net, high_net); bars from the worse to the better
    value around the base line; orange = the bad side, blue = the good side."""
    lo = min(min(r[1], r[3]) for r in rows)
    hi = max(max(r[1], r[3]) for r in rows)
    pad = (hi - lo) * 0.04
    lo, hi = lo - pad, hi + pad
    x = lambda v: (v - lo) / (hi - lo) * track_w
    out = []
    for label, a, b, c in rows:
        worse, better = min(a, c), max(a, c)
        bars = (f'<div style="position:absolute;left:{x(worse):.0f}px;top:4px;width:{max(2, x(b) - x(worse)):.0f}px;height:32px;background:{ORANGE}"></div>'
                f'<div style="position:absolute;left:{x(b):.0f}px;top:4px;width:{max(2, x(better) - x(b)):.0f}px;height:32px;background:{BLUE}"></div>'
                f'<div style="position:absolute;left:{x(b) - 1:.0f}px;top:0px;width:3px;height:40px;background:{INK}"></div>')
        out.append(f'<div style="display:flex;gap:16px;align-items:center">'
                   f'<p style="width:{label_w}px;font-size:24px;color:{INK}">{label}</p>'
                   f'<div style="position:relative;width:{track_w}px;height:40px">{bars}</div>'
                   f'<p style="width:{value_w}px;font-size:24px;color:{MUTED};white-space:nowrap">{fmt(worse)} to {fmt(better)}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:14px">{"".join(out)}</div>'


def share_bars(rows, label_w=520, track_w=900, color=BLUE, fmt=lambda v: f"{v:.0%}"):
    """rows: list of (label, value 0..1, display or None[, colour])."""
    top = max(r[1] for r in rows)
    out = []
    for row in rows:
        label, v, disp = row[:3]
        c = row[3] if len(row) > 3 else color
        out.append(f'<div style="display:flex;gap:20px;align-items:center">'
                   f'<p style="width:{label_w}px;font-size:28px;color:{INK}">{label}</p>'
                   f'<div style="width:{max(4, v / top * track_w):.0f}px;height:36px;background:{c};border-radius:4px"></div>'
                   f'<p style="font-size:32px;font-weight:600;color:{INK};white-space:nowrap">{disp or fmt(v)}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:16px">{"".join(out)}</div>'


def _shade(v, vmax):
    """Diverging fill: orange for losses, blue for gains, stronger with size."""
    t = min(1.0, abs(v) / vmax) if vmax else 0
    if v < 0:
        a = (0xF6, 0xE3, 0xD0); b = (0xB8, 0x5A, 0x14)
    else:
        a = (0xDC, 0xE7, 0xF3); b = (0x2F, 0x66, 0xA8)
    c = tuple(int(a[i] + (b[i] - a[i]) * t) for i in range(3))
    return "#%02X%02X%02X" % c, (PAPER if t > 0.55 else INK)


def heatmap(row_labels, col_labels, values, fmt, row_head="", col_head="", cell_w=230, cell_h=72, label_w=300):
    vmax = max(abs(v) for row in values for v in row)
    head = (f'<div style="display:flex;gap:6px"><p style="width:{label_w}px;font-size:24px;color:{MUTED}">{row_head}</p>'
            + "".join(f'<p style="width:{cell_w}px;font-size:24px;color:{MUTED};text-align:center">{c}</p>' for c in col_labels) + "</div>")
    rows = []
    for lab, vals in zip(row_labels, values):
        cells = []
        for v in vals:
            bg, fg = _shade(v, vmax)
            cells.append(f'<div style="width:{cell_w}px;height:{cell_h}px;background:{bg};border-radius:6px;display:flex;align-items:center;justify-content:center">'
                         f'<p style="font-size:26px;font-weight:600;color:{fg}">{fmt(v)}</p></div>')
        rows.append(f'<div style="display:flex;gap:6px;align-items:center"><p style="width:{label_w}px;font-size:26px;color:{INK}">{lab}</p>{"".join(cells)}</div>')
    top = f'<p style="font-size:24px;color:{MUTED}">{col_head}</p>' if col_head else ""
    return f'<div style="display:flex;flex-direction:column;gap:6px">{top}{head}{"".join(rows)}</div>'


def dist_svg(dist, low, mode, high, w=360, h=110, color=BLUE):
    """A small density curve for one input's distribution (triangular or lognormal)."""
    if dist == "triangular":
        pts = [(0, h), ((mode - low) / (high - low) * w if high > low else w / 2, 4), (w, h)]
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        lo_x, hi_x = low, high
    else:  # lognormal from P5 = low, P95 = high
        mu = (math.log(low) + math.log(high)) / 2
        sg = (math.log(high) - math.log(low)) / (2 * 1.6448536)
        lo_x, hi_x = math.exp(mu - 2.6 * sg), math.exp(mu + 2.6 * sg)
        xs = np.linspace(lo_x, hi_x, 60)
        ys = stats.lognorm.pdf(xs, sg, scale=math.exp(mu))
        ys = ys / ys.max()
        pts = [(0, h)] + [((x - lo_x) / (hi_x - lo_x) * w, h - y * (h - 4)) for x, y in zip(xs, ys)] + [(w, h)]
        poly = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
    return (f'<svg aria-label="distribution" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
            f'<polygon points="{poly}" fill="{color}" fill-opacity="0.35" stroke="{color}" stroke-width="3"/></svg>')


def staircase(steps, start, fmt, width=1664, height=380, label_w=None):
    """Waterfall rising from `start` (a loss) to break-even: steps = list of (label, value_after)."""
    n = len(steps)
    gap = 14
    cw = (width - gap * (n - 1)) / n
    lo, hi = min(start, min(v for _, v in steps)), max(0.0, max(v for _, v in steps))
    y = lambda v: (hi - v) / (hi - lo) * height
    cols = []
    prev = start
    for i, (label, v) in enumerate(steps):
        top, bot = y(max(prev, v)), y(min(prev, v))
        color = BLUE if v >= 0 else LBLUE
        cols.append(f'<div style="width:{cw:.1f}px;display:flex;flex-direction:column;gap:8px">'
                    f'<div style="position:relative;width:{cw:.1f}px;height:{height}px">'
                    f'<div style="position:absolute;left:0px;top:{top:.0f}px;width:{cw:.1f}px;height:{max(3, bot - top):.0f}px;background:{color};border-radius:4px"></div>'
                    f'<div style="position:absolute;left:0px;top:{y(0) - 1:.0f}px;width:{cw:.1f}px;height:3px;background:{INK}"></div></div>'
                    f'<p style="font-size:24px;line-height:1.2;color:{INK};text-align:center">{i + 1}</p></div>')
        prev = v
    return f'<div style="display:flex;gap:{gap}px">{"".join(cols)}</div>'


# ---------------------------------------------------------------- more components for the evidence deck
def histogram_marked(bins, width=1664, height=340, markers=(), zero_label="break-even", first_row=0):
    """Histogram whose x-range always reaches 0 (empty bins up to it), with a break-even line and
    labelled markers: markers = list of (value, label)."""
    bins = list(bins)
    step = bins[0][1] - bins[0][0]
    while bins[-1][1] < step * 0.6:
        bins.append((bins[-1][1], bins[-1][1] + step, 0.0))
    n = len(bins)
    gap = 3
    bw = (width - gap * (n - 1)) / n
    top = max(b[2] for b in bins)
    bars = "".join(f'<div style="width:{bw:.1f}px;height:{max(2, b[2] / top * (height - 60)):.0f}px;background:{ORANGE if b[1] <= 0 else BLUE};border-radius:3px 3px 0 0"></div>' for b in bins)
    lo, hi = bins[0][0], bins[-1][1]
    x = lambda v: (v - lo) / (hi - lo) * width
    pins = [f'<div style="position:absolute;left:{x(0) - 2:.0f}px;top:0px;width:4px;height:{height}px;background:{INK}"></div>',
            f'<p style="position:absolute;left:{max(0, x(0) - 200):.0f}px;top:{height + 8}px;width:200px;font-size:24px;font-weight:600;color:{INK};text-align:right">{zero_label}</p>']
    for k, (v, label) in enumerate(markers):
        pins.append(f'<div style="position:absolute;left:{x(v) - 1:.0f}px;top:0px;width:2px;height:{height}px;background:{MUTED}"></div>')
        pins.append(f'<p style="position:absolute;left:{min(width - 440, max(0, x(v) - 220)):.0f}px;top:{height + 8 + ((k + first_row) % 2) * 34}px;width:440px;font-size:24px;color:{MUTED};text-align:center;white-space:nowrap">{label}</p>')
    return (f'<div style="position:relative;width:{width}px;height:{height + 80}px">'
            f'<div style="display:flex;gap:{gap}px;align-items:flex-end;height:{height}px">{bars}</div>{"".join(pins)}</div>')


def tornado_zero(rows, label_w=430, track_w=980, value_w=230):
    """rows: (label, low_net, centre_net, high_net, display_text); the axis always reaches 0 (break-even)."""
    lo = min(min(r[1], r[3]) for r in rows)
    hi = max(0.0, max(max(r[1], r[3]) for r in rows))
    pad = (hi - lo) * 0.03
    lo, hi = lo - pad, hi + pad
    x = lambda v: (v - lo) / (hi - lo) * track_w
    out = []
    for label, a, b, c, disp in rows:
        worse, better = min(a, c), max(a, c)
        bars = (f'<div style="position:absolute;left:{x(worse):.0f}px;top:6px;width:{max(2, x(b) - x(worse)):.0f}px;height:28px;background:{ORANGE}"></div>'
                f'<div style="position:absolute;left:{x(b):.0f}px;top:6px;width:{max(2, x(better) - x(b)):.0f}px;height:28px;background:{BLUE}"></div>'
                f'<div style="position:absolute;left:{x(0) - 2:.0f}px;top:0px;width:4px;height:40px;background:{INK}"></div>')
        out.append(f'<div style="display:flex;gap:16px;align-items:center"><p style="width:{label_w}px;font-size:24px;color:{INK}">{label}</p>'
                   f'<div style="position:relative;width:{track_w}px;height:40px">{bars}</div>'
                   f'<p style="width:{value_w}px;font-size:24px;color:{MUTED};white-space:nowrap">{disp}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:12px">{"".join(out)}</div>'


def ranges(rows, width=1100, label_w=360, value_w=200):
    """rows: (label, p5, p50, p95, text); a band from P5 to P95 with a median tick; axis reaches 0."""
    lo = min(r[1] for r in rows)
    hi = max(0.0, max(r[3] for r in rows))
    pad = (hi - lo) * 0.05
    lo, hi = lo - pad, hi + pad
    x = lambda v: (v - lo) / (hi - lo) * width
    out = []
    for label, a, m, c, txt in rows:
        pins = (f'<div style="position:absolute;left:{x(a):.0f}px;top:14px;width:{max(4, x(c) - x(a)):.0f}px;height:32px;background:{LBLUE};border-radius:6px"></div>'
                f'<div style="position:absolute;left:{x(m) - 3:.0f}px;top:4px;width:6px;height:52px;background:{INK}"></div>'
                f'<div style="position:absolute;left:{x(0) - 2:.0f}px;top:0px;width:4px;height:60px;background:{ORANGE}"></div>')
        out.append(f'<div style="display:flex;gap:20px;align-items:center"><p style="width:{label_w}px;font-size:28px;color:{INK}">{label}</p>'
                   f'<div style="position:relative;width:{width}px;height:60px">{pins}</div>'
                   f'<p style="width:{value_w}px;font-size:24px;color:{MUTED}">{txt}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:28px">{"".join(out)}</div>'


def dot_grid(groups, per_row=10, size=56, gap=14):
    """groups: list of (count, color); one painted dot per item, in rows."""
    dots = []
    for count, color in groups:
        dots += [color] * count
    rows = [dots[i:i + per_row] for i in range(0, len(dots), per_row)]
    return ('<div style="display:flex;flex-direction:column;gap:%dpx">' % gap + "".join(
        f'<div style="display:flex;gap:{gap}px">' + "".join(
            f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{c}"></div>' for c in row) + "</div>" for row in rows) + "</div>")


def steps_bars(steps, width=1664, height=360, gap=28):
    """A walk from a starting value through labelled steps: steps = list of (label, value, display);
    the first is the start. Bars float between consecutive values; an ink line marks zero."""
    n = len(steps)
    cw = (width - gap * (n - 1)) / n
    vals = [v for _, v, _ in steps]
    lo, hi = min(min(vals), 0.0), max(max(vals), 0.0)
    pad = (hi - lo) * 0.06
    lo, hi = lo - pad, hi + pad
    y = lambda v: (hi - v) / (hi - lo) * height
    cols = []
    prev = None
    for i, (label, v, disp) in enumerate(steps):
        a, b = (0.0, v) if prev is None else (prev, v)
        top, bot = y(max(a, b)), y(min(a, b))
        color = (ORANGE if v < 0 else BLUE) if prev is None else (BLUE if v >= prev else ORANGE)
        cols.append(f'<div style="width:{cw:.0f}px;display:flex;flex-direction:column;gap:10px">'
                    f'<div style="position:relative;width:{cw:.0f}px;height:{height}px">'
                    f'<div style="position:absolute;left:{cw * 0.15:.0f}px;top:{top:.0f}px;width:{cw * 0.7:.0f}px;height:{max(3, bot - top):.0f}px;background:{color};border-radius:4px"></div>'
                    f'<div style="position:absolute;left:0px;top:{y(0) - 2:.0f}px;width:{cw:.0f}px;height:4px;background:{INK}"></div></div>'
                    f'<p style="font-size:28px;font-weight:600;color:{ORANGE if v < 0 else BLUE};text-align:center">{disp}</p>'
                    f'<p style="font-size:24px;line-height:1.25;color:{INK};text-align:center">{label}</p></div>')
        prev = v
    return f'<div style="display:flex;gap:{gap}px">{"".join(cols)}</div>'


def dist_with_markers(dist, low, mode, high, markers, w=1500, h=230, color=BLUE):
    """A density curve with labelled vertical markers: markers = list of (value, label, colour)."""
    if dist == "lognormal":
        mu = (math.log(low) + math.log(high)) / 2
        sg = (math.log(high) - math.log(low)) / (2 * 1.6448536)
        lo_x, hi_x = math.exp(mu - 2.3 * sg), math.exp(mu + 2.3 * sg)
    else:
        lo_x, hi_x = low, high
    svg = dist_svg(dist, low, mode, high, w=w, h=h, color=color) if dist != "lognormal" else None
    if dist == "lognormal":
        xs = np.linspace(lo_x, hi_x, 80)
        ys = stats.lognorm.pdf(xs, sg, scale=math.exp(mu))
        ys = ys / ys.max()
        pts = [(0, h)] + [((xx - lo_x) / (hi_x - lo_x) * w, h - yy * (h - 6)) for xx, yy in zip(xs, ys)] + [(w, h)]
        svg = (f'<svg aria-label="distribution" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
               f'<polygon points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in pts)}" fill="{color}" fill-opacity="0.3" stroke="{color}" stroke-width="3"/></svg>')
    x = lambda v: (min(max(v, lo_x), hi_x) - lo_x) / (hi_x - lo_x) * w
    pins = []
    for k, (v, label, col) in enumerate(markers):
        pins.append(f'<div style="position:absolute;left:{x(v) - 2:.0f}px;top:0px;width:4px;height:{h}px;background:{col}"></div>')
        pins.append(f'<p style="position:absolute;left:{min(w - 360, max(0, x(v) - 180)):.0f}px;top:{h + 8 + (k % 2) * 36}px;width:360px;font-size:24px;font-weight:600;color:{col};text-align:center">{label}</p>')
    return (f'<div style="position:relative;width:{w}px;height:{h + 84}px">{svg}{"".join(pins)}</div>')


def dots(n_on, color, n=10, size=44):
    return ('<div style="display:flex;gap:12px">'
            + "".join(f'<div style="width:{size}px;height:{size}px;border-radius:50%;background:{color if k < n_on else LIGHT}"></div>' for k in range(n))
            + "</div>")


def waterfall(rows, label_w=600, track_w=820, bar_h=48):
    """Horizontal waterfall. rows: (label, delta, display, kind) with kind 'cost' | 'income' | 'total'
    (a total bar runs from zero to the running sum)."""
    cum, spans = 0.0, []
    for label, delta, disp, kind in rows:
        if kind == "total":
            spans.append((0.0, cum))
        else:
            spans.append((cum, cum + delta))
            cum += delta
    lo = min(0.0, min(min(a, b) for a, b in spans))
    hi = max(0.0, max(max(a, b) for a, b in spans))
    pad = (hi - lo) * 0.02
    lo, hi = lo - pad, hi + pad
    x = lambda v: (v - lo) / (hi - lo) * track_w
    col = {"cost": ORANGE, "income": BLUE, "total": INK}
    out = []
    for (label, delta, disp, kind), (a, b) in zip(rows, spans):
        left, w = min(x(a), x(b)), max(4, abs(x(b) - x(a)))
        out.append(f'<div style="display:flex;gap:20px;align-items:center">'
                   f'<p style="width:{label_w}px;font-size:28px;line-height:1.25;color:{INK};{"font-weight:600" if kind == "total" else ""}">{label}</p>'
                   f'<div style="position:relative;width:{track_w}px;height:{bar_h + 20}px">'
                   f'<div style="position:absolute;left:{x(0) - 1:.0f}px;top:0px;width:3px;height:{bar_h + 20}px;background:{MUTED}"></div>'
                   f'<div style="position:absolute;left:{left:.0f}px;top:10px;width:{w:.0f}px;height:{bar_h}px;background:{col[kind]};border-radius:4px"></div></div>'
                   f'<p style="width:150px;font-size:32px;font-weight:600;color:{INK};white-space:nowrap">{disp}</p></div>')
    return f'<div style="display:flex;flex-direction:column;gap:0px">{"".join(out)}</div>'


def lines(series, x_max, width=1664, height=440, right=420, x_ticks=(), zero_label="break-even", marks=()):
    """Line chart: the lines are SVG, every label is slide text (an SVG becomes an image, which cannot
    use the deck's fonts). series: (label, [(x, y)], colour, dashed); x_ticks: (x, text);
    marks: (x, y, text) dots with a label. Labels sit at each line's right end."""
    ys = [y for _, pts, _, _ in series for _, y in pts] + [0.0]
    lo, hi = min(ys), max(ys)
    pad = (hi - lo) * 0.06
    lo, hi = lo - pad, hi + pad
    W, H = width - right, height - 50
    X = lambda v: v / x_max * W
    Y = lambda v: (hi - v) / (hi - lo) * H
    el = [f'<line x1="0" y1="{Y(0):.1f}" x2="{W}" y2="{Y(0):.1f}" stroke="{INK}" stroke-width="3"/>']
    for label, pts, colr, dashed in series:
        d = " ".join(f"{'M' if i == 0 else 'L'}{X(a):.1f},{Y(b):.1f}" for i, (a, b) in enumerate(pts))
        el.append(f'<path d="{d}" fill="none" stroke="{colr}" stroke-width="5"{" stroke-dasharray=\"14 10\"" if dashed else ""}/>')
    svg = f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" style="position:absolute;left:0px;top:0px">{"".join(el)}</svg>'
    txt = lambda x, y, t, c, w=360, bold=True, align="left": (f'<p style="position:absolute;left:{x:.0f}px;top:{y:.0f}px;width:{w}px;font-size:24px;line-height:1.2;'
                                                               f'{"font-weight:600;" if bold else ""}color:{c};text-align:{align};white-space:nowrap">{t}</p>')
    pins = []
    ends = [[Y(pts[-1][1]) - 14, label, colr] for label, pts, colr, _ in series] + [[Y(0) - 14, zero_label, INK]]
    ends.sort()
    for i in range(1, len(ends)):                      # keep end labels 32px apart
        ends[i][0] = max(ends[i][0], ends[i - 1][0] + 32)
    for yv, label, colr in ends:
        pins.append(txt(W + 16, yv, label, colr))
    for xv, t in x_ticks:
        pins.append(txt(X(xv) - 60, H + 14, t, MUTED, w=120, bold=False, align="center"))
    for xv, yv, t in marks:
        pins.append(f'<div style="position:absolute;left:{X(xv) - 10:.0f}px;top:{Y(yv) - 10:.0f}px;width:20px;height:20px;border-radius:10px;background:{INK}"></div>')
        pins.append(txt(X(xv) + 18, Y(yv) + 12, t, INK, w=200))
    return f'<div style="position:relative;width:{width}px;height:{height}px">{svg}{"".join(pins)}</div>'

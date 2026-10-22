"""The QR-moat test as a PICTURE story (operator, 12 Oct 2026: "the pdf has a lot of text. provide me a
pdf with clean chart, diagram, flowchart, pictures that makes me understand the story in a tighter way").

One page = one sentence + one visual + its source ids. Same evidence and numbers as build_qr_pdf.py:
quotes only tables/qr_moat_numbers.csv and research/qr_moat.csv. Writes brief/qr_moat/qr_moat_visual.html
and prints it to QR_moat_story.pdf (A4 landscape) with Chrome.
"""
import csv
import html
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NUM = {r["key"]: float(r["value"]) for r in csv.DictReader((ROOT / "tables" / "qr_moat_numbers.csv").open())}
EV = list(csv.DictReader((ROOT / "research" / "qr_moat.csv").open()))
OUT_DIR = ROOT / "brief" / "qr_moat"
PDF = ROOT / "QR_moat_story.pdf"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

INK, MUTED, RULE, PAPER = "#1f2328", "#5b636c", "#e3ded4", "#f7f5f0"
THEM, US, GREY = "#1F64A8", "#8A3B08", "#B9AE9B"          # validated pair (dataviz validator, light)
GOOD, WARN, BAD = "#2f6b4f", "#9a6700", "#b42318"
TINT = {"good": "#e6f2ea", "warn": "#fbf1dc", "bad": "#f8e6e3", "down": "#e6eef7", "flat": "#e6eef7"}
MARK = {"good": "✓", "warn": "!", "bad": "✕", "down": "↓", "flat": "→"}
COL = {"good": GOOD, "warn": WARN, "bad": BAD, "down": THEM, "flat": THEM}
TOTAL = 9


def n(k):
    return NUM[k]


def pct(k, d=0):
    return f"{n(k) * 100:.{d}f}%"


def rs(x):
    return f"₹{x:,.0f}"


# ---------- drawing helpers ----------
def text(x, y, s, size=14, weight=400, fill=INK, anchor="start", lh=None):
    lines = s.split("|")
    lh = lh or size * 1.25
    return "".join(f'<text x="{x}" y="{y + i * lh}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{html.escape(t)}</text>'
                   for i, t in enumerate(lines))


def icon(name, x, y, s, c):
    """Simple flat pictures on a 48-unit grid, placed at (x, y) with size s."""
    g = {
        "qr": (f'<rect x="4" y="4" width="40" height="40" rx="4" fill="#fff" stroke="{c}" stroke-width="2.5"/>'
               + "".join(f'<rect x="{a}" y="{b}" width="12" height="12" rx="1.5" fill="{c}"/><rect x="{a + 2.5}" y="{b + 2.5}" width="7" height="7" fill="#fff"/><rect x="{a + 4}" y="{b + 4}" width="4" height="4" fill="{c}"/>'
                         for a, b in ((8, 8), (28, 8), (8, 28)))
               + "".join(f'<rect x="{a}" y="{b}" width="4" height="4" fill="{c}"/>' for a, b in ((28, 28), (34, 28), (38, 34), (30, 36), (36, 40), (28, 40), (22, 22), (22, 10), (16, 22)))),
        "speaker": (f'<rect x="11" y="5" width="26" height="38" rx="7" fill="{c}"/><circle cx="24" cy="21" r="8" fill="#fff"/><circle cx="24" cy="21" r="3" fill="{c}"/>'
                    f'<rect x="17" y="34" width="14" height="3" rx="1.5" fill="#fff"/>'
                    f'<path d="M41,14 q5,10 0,20" fill="none" stroke="{c}" stroke-width="2.5" stroke-linecap="round"/>'),
        "till": (f'<rect x="9" y="8" width="30" height="9" rx="2" fill="{c}" opacity="0.55"/><rect x="4" y="19" width="40" height="23" rx="4" fill="{c}"/>'
                 f'<rect x="16" y="27" width="16" height="3" rx="1.5" fill="#fff"/><text x="24" y="16" font-size="8" font-weight="700" fill="#fff" text-anchor="middle">₹</text>'),
        "jar": (f'<rect x="15" y="5" width="18" height="6" rx="2" fill="{c}"/><path d="M12,14 h24 q4,0 4,6 v18 q0,6 -6,6 h-20 q-6,0 -6,-6 v-18 q0,-6 4,-6 z" fill="{c}"/>'
                f'<circle cx="24" cy="29" r="8" fill="#fff"/><text x="24" y="33.5" font-size="11" font-weight="700" fill="{c}" text-anchor="middle">₹</text>'),
        "person": f'<circle cx="24" cy="14" r="8" fill="{c}"/><path d="M8,44 q0,-18 16,-18 q16,0 16,18 z" fill="{c}"/>',
        "bank": (f'<path d="M4,17 L24,5 L44,17 Z" fill="{c}"/>'
                 + "".join(f'<rect x="{a}" y="20" width="5" height="17" fill="{c}"/>' for a in (8, 17, 26, 35))
                 + f'<rect x="4" y="39" width="40" height="5" rx="1" fill="{c}"/>'),
        "phone": f'<rect x="13" y="3" width="22" height="42" rx="5" fill="{c}"/><rect x="16" y="8" width="16" height="28" rx="1.5" fill="#fff"/><circle cx="24" cy="40" r="2" fill="#fff"/>',
        "coin": f'<circle cx="24" cy="24" r="19" fill="{c}"/><circle cx="24" cy="24" r="14" fill="none" stroke="#fff" stroke-width="2"/><text x="24" y="31" font-size="19" font-weight="700" fill="#fff" text-anchor="middle">₹</text>',
        "pct": f'<circle cx="24" cy="24" r="19" fill="{c}"/><text x="24" y="31.5" font-size="20" font-weight="700" fill="#fff" text-anchor="middle">%</text>',
        "broken": (f'<circle cx="24" cy="24" r="19" fill="{c}"/><path d="M22,5 l5,10 l-6,7 l7,8 l-5,13" fill="none" stroke="#fff" stroke-width="3" stroke-linejoin="round"/>'),
        "hands": (f'<circle cx="16" cy="13" r="6" fill="{c}"/><path d="M5,42 q0,-15 11,-15 q11,0 11,15 z" fill="{c}"/>'
                  f'<circle cx="34" cy="13" r="6" fill="{c}" opacity="0.5"/><path d="M23,42 q0,-15 11,-15 q11,0 11,15 z" fill="{c}" opacity="0.5"/>'),
        "doc": (f'<path d="M10,4 h20 l9,9 v31 h-29 z" fill="{c}"/><path d="M30,4 v9 h9" fill="#fff" opacity="0.5"/>'
                + "".join(f'<rect x="15" y="{y0}" width="19" height="2.5" rx="1" fill="#fff"/>' for y0 in (20, 26, 32))),
    }[name]
    return f'<g transform="translate({x},{y}) scale({s / 48})">{g}</g>'


def badge(x, y, kind, label, size=15, anchor="middle"):
    w = len(label) * size * 0.56 + size * 2.2
    x0 = x - w / 2 if anchor == "middle" else x
    r = size * 0.62
    return (f'<rect x="{x0}" y="{y - size * 1.05}" width="{w}" height="{size * 1.6}" rx="{size * 0.8}" fill="{TINT[kind]}"/>'
            f'<circle cx="{x0 + size * 0.85}" cy="{y - size * 0.25}" r="{r}" fill="{COL[kind]}"/>'
            f'<text x="{x0 + size * 0.85}" y="{y + size * 0.12}" font-size="{size * 0.8}" font-weight="700" fill="#fff" text-anchor="middle">{MARK[kind]}</text>'
            f'<text x="{x0 + size * 1.75}" y="{y + size * 0.2}" font-size="{size}" font-weight="700" fill="{COL[kind]}">{html.escape(label)}</text>')


def arrow(x1, y1, x2, y2, c=MUTED, w=2):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 10 * math.cos(a), y2 - 10 * math.sin(a)
    px, py = 5 * math.sin(a), -5 * math.cos(a)
    return (f'<line x1="{x1}" y1="{y1}" x2="{hx}" y2="{hy}" stroke="{c}" stroke-width="{w}"/>'
            f'<path d="M{x2},{y2} L{hx + px},{hy + py} L{hx - px},{hy - py} Z" fill="{c}"/>')


def node(x, y, w, h, ic, ic_c, title, sub="", hl=None, fill="#fff"):
    stroke = hl or RULE
    s = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill if not hl else "#fff"}" stroke="{stroke}" stroke-width="{3 if hl else 1.5}"/>']
    if ic:
        s.append(icon(ic, x + 12, y + (h - 38) / 2, 38, ic_c))
        tx = x + 60
    else:
        tx = x + 14
    s.append(text(tx, y + h / 2 - (6 if sub else -5), title, 15, 700))
    if sub:
        s.append(text(tx, y + h / 2 + 14, sub, 12.5, 400, MUTED, lh=15))
    return "".join(s)


def diamond(cx, cy, w, h, label, c=INK):
    return (f'<path d="M{cx},{cy - h / 2} L{cx + w / 2},{cy} L{cx},{cy + h / 2} L{cx - w / 2},{cy} Z" fill="#fff" stroke="{c}" stroke-width="2"/>'
            + text(cx, cy - (7 if "|" in label else -5), label, 13.5, 700, c, "middle", 16))


def bars(vals, labels, texts, colours, w, h, top=34, bottom=46, fs=17, hatch_last=False):
    k, gap = len(vals), 22
    bw = (w - gap * (k + 1)) / k
    plot, vmax = h - top - bottom, max(vals)
    s = [f'<line x1="0" y1="{h - bottom}" x2="{w}" y2="{h - bottom}" stroke="{MUTED}" stroke-width="1"/>']
    for i, (v, lab, t, c) in enumerate(zip(vals, labels, texts, colours)):
        bh = max(plot * v / vmax, 3)
        x, y = gap + i * (bw + gap), h - bottom - bh
        r = min(4, bw / 2, bh)
        fill = "url(#hatch)" if hatch_last and i == k - 1 else c
        s.append(f'<path d="M{x},{h - bottom} V{y + r} Q{x},{y} {x + r},{y} H{x + bw - r} Q{x + bw},{y} {x + bw},{y + r} V{h - bottom} Z" fill="{fill}"/>')
        s.append(text(x + bw / 2, y - 9, t, fs, 700, INK, "middle"))
        s.append(text(x + bw / 2, h - bottom + 20, lab, 13, 400, MUTED, "middle", 15))
    return "".join(s)


def svg(w, h, body):
    defs = (f'<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
            f'<rect width="7" height="7" fill="{THEM}" opacity="0.25"/><line x1="0" y1="0" x2="0" y2="7" stroke="{THEM}" stroke-width="3"/></pattern></defs>')
    return f'<svg viewBox="0 0 {w} {h}" width="100%" role="img">{defs}{body}</svg>'


# ---------- pages ----------
def p_answer():
    cards = [
        ("qr", THEM, "The QR code", "good", "Easy to copy", f"≈{n('qr_per_merchant'):.0f}", "QR codes on|the average shop"),
        ("speaker", THEM, "The soundbox", "warn", "Sticky", f"{n('paytm_dev_mar24'):.2f} cr", "Paytm shops kept paying|through the 2024 shock"),
        ("till", THEM, "The till", "bad", "Hard to beat", f"{pct('paytm_ecl_low', 1)}–{pct('paytm_ecl_high', 0)}", "their losses: repaid from|the shop's daily payout"),
        ("jar", US, "Our savings hook", "bad", "Already copied", "₹100/day", "PhonePe deposit,|launched 6 Aug 2026"),
    ]
    s = [text(0, 22, "WHAT PAYTM AND PHONEPE HOLD", 13, 700, THEM), text(770, 22, "OUR WAY IN", 13, 700, US)]
    for i, (ic, c, name, kind, chip, big, sub) in enumerate(cards):
        x = i * 240 + (30 if i == 3 else 0)
        s.append(f'<rect x="{x}" y="40" width="220" height="330" rx="16" fill="{PAPER}"/>')
        s.append(icon(ic, x + 78, 62, 64, c))
        s.append(text(x + 110, 160, name, 20, 700, INK, "middle"))
        s.append(badge(x + 110, 200, kind, chip, 15))
        s.append(text(x + 110, 262, big, 34, 800, c, "middle"))
        s.append(text(x + 110, 292, sub, 14, 400, MUTED, "middle", 18))
    s.append(f'<line x1="740" y1="40" x2="740" y2="370" stroke="{RULE}" stroke-width="2" stroke-dasharray="6 6"/>')
    s.append(arrow(20, 400, 690, 400, MUTED, 2.5))
    s.append(text(20, 425, "easy to take", 13, 600, MUTED))
    s.append(text(690, 425, "hard to take", 13, 600, MUTED, "end"))
    return svg(1000, 440, "".join(s))


def p_qr():
    s = []
    # the shop: awning, back wall, shopkeeper, counter with 9 QR stickers and a soundbox
    for i in range(10):
        s.append(f'<rect x="{20 + i * 52}" y="20" width="52" height="38" fill="{US if i % 2 == 0 else "#f0e4d6"}"/>')
    s.append(f'<path d="M20,58 ' + " ".join(f"q13,16 26,0 q13,16 26,0" for _ in range(10)) + f'" fill="{US}" opacity="0.9"/>')
    s.append(f'<rect x="28" y="74" width="504" height="120" fill="{PAPER}"/>')
    s.append(icon("person", 240, 104, 84, "#9b8f7d"))
    s.append(f'<rect x="20" y="190" width="520" height="160" rx="6" fill="#e9e3d8" stroke="#d6cdbd"/>')
    s.append(icon("speaker", 430, 140, 50, THEM))
    for i in range(9):
        r, c = divmod(i, 5)
        x = 52 + c * 92 + (46 if r == 1 else 0)
        y = 212 + r * 66
        s.append(f'<rect x="{x - 4}" y="{y - 4}" width="62" height="62" rx="6" fill="#fff" stroke="#d6cdbd"/>')
        s.append(icon("qr", x + 3, y + 3, 48, THEM))
    # the stat
    s.append(text(800, 150, f"≈{n('qr_per_merchant'):.0f}", 120, 800, THEM, "middle"))
    s.append(text(800, 195, "QR codes per shop", 22, 700, INK, "middle"))
    s.append(text(800, 222, f"{n('qr_codes_cr'):.1f} crore codes ÷ 6.5 crore shops (FY25)", 14, 400, MUTED, "middle"))
    # a newcomer did it
    s.append(f'<rect x="610" y="262" width="380" height="88" rx="14" fill="{PAPER}"/>')
    s.append(text(630, 290, "A newcomer did it: BharatPe", 15, 700))
    s.append(text(630, 326, "2018", 22, 800, MUTED))
    s.append(text(630, 342, "0 shops", 12, 400, MUTED))
    s.append(arrow(700, 318, 830, 318, US, 3))
    s.append(text(850, 326, "1.3 cr+", 22, 800, US))
    s.append(text(850, 342, "shops by 2025", 12, 400, MUTED))
    return svg(1000, 360, "".join(s))


def p_shock():
    charts = [
        ("person", "Customers", "Paytm app's share of UPI payments",
         [n("paytm_share_dec23"), n("paytm_share_dec24")], ["Dec 2023", "Dec 2024"],
         [f"{n('paytm_share_dec23'):.1f}%", f"{n('paytm_share_dec24'):.1f}%"], "down", "Left"),
        ("speaker", "Shops", "Shops paying for a Paytm device, crore",
         [n("paytm_dev_dec23"), n("paytm_dev_mar24"), n("paytm_dev_mar26"), n("paytm_dev_jun26")], ["Dec|2023", "Mar|2024", "Mar|2026", "Jun|2026"],
         [f"{n(k):.2f}" for k in ("paytm_dev_dec23", "paytm_dev_mar24", "paytm_dev_mar26", "paytm_dev_jun26")], "flat", "Stayed"),
        ("bank", "Loans", "Paytm shop loans, ₹ crore a quarter",
         [n("paytm_ml_q3fy24"), n("paytm_ml_q4fy24")], ["Oct–Dec|2023", "Jan–Mar|2024"],
         [rs(n("paytm_ml_q3fy24")), rs(n("paytm_ml_q4fy24"))], "down", "Halved"),
    ]
    s = []
    for i, (ic, who, title, vals, labs, txt, kind, verdict) in enumerate(charts):
        x = i * 340
        s.append(f'<rect x="{x}" y="0" width="315" height="420" rx="16" fill="{PAPER}"/>')
        s.append(icon(ic, x + 20, 18, 40, THEM))
        s.append(text(x + 72, 38, who, 20, 700))
        s.append(text(x + 72, 58, title, 12, 400, MUTED))
        colours = [GREY] + [THEM] * (len(vals) - 1)
        s.append(f'<g transform="translate({x + 15},78)">{bars(vals, labs, txt, colours, 285, 250)}</g>')
        s.append(badge(x + 157, 385, kind, verdict, 19))
    s.append(f'<rect x="0" y="438" width="14" height="14" rx="3" fill="{GREY}"/>' + text(20, 450, "before the RBI action (Jan 2024)", 13, 400, MUTED))
    s.append(f'<rect x="260" y="438" width="14" height="14" rx="3" fill="{THEM}"/>' + text(280, 450, "after", 13, 400, MUTED))
    return svg(1000, 460, "".join(s))


def p_paid_first():
    s = [text(0, 20, "THEIR SHOP LOAN", 14, 700, THEM), text(0, 230, "OUR SHOP LOAN", 14, 700, US)]
    xs, w, h = (0, 180, 360, 540), 160, 84
    a = [("person", INK, "Customer|pays ₹500", ""), ("qr", THEM, "Their QR", "sees every|rupee"),
         ("till", THEM, "Instalment|cut first", ""), ("bank", MUTED, "Rest paid|to the shop", "")]
    for i, (ic, c, t, sub) in enumerate(a):
        s.append(node(xs[i], 40, w, h, ic, c, t, sub, THEM if i == 2 else None))
        if i < 3:
            s.append(arrow(xs[i] + w + 2, 82, xs[i + 1] - 4, 82))
    s.append(arrow(xs[3] + w + 2, 82, 760, 82, THEM, 2.5))
    s.append(f'<rect x="762" y="52" width="230" height="60" rx="30" fill="{THEM}"/>')
    s.append(text(877, 78, "Paid first,", 17, 700, "#fff", "middle"))
    s.append(text(877, 99, "every single day", 14, 400, "#fff", "middle"))

    b = [("person", INK, "Customer|pays ₹500", ""), ("qr", MUTED, "Any QR", "we see|nothing"),
         ("bank", MUTED, "All ₹500 paid|to the shop", ""), ("jar", US, "Next day we", "ask by Autopay")]
    for i, (ic, c, t, sub) in enumerate(b):
        s.append(node(xs[i], 250, w, h, ic, c, t, sub, US if i == 3 else None))
        if i < 3:
            s.append(arrow(xs[i] + w + 2, 292, xs[i + 1] - 4, 292))
    s.append(arrow(xs[3] + w + 2, 292, 742, 292))
    s.append(diamond(810, 292, 136, 96, "Money still|there?", US))
    s.append(arrow(878, 292, 905, 250, GOOD))
    s.append(text(912, 250, "Yes: paid", 15, 700, GOOD))
    s.append(arrow(878, 292, 905, 340, BAD))
    s.append(text(912, 342, "No: missed", 15, 700, BAD))
    s.append(f'<rect x="560" y="370" width="432" height="58" rx="12" fill="{TINT["bad"]}"/>')
    s.append(text(776, 395, f"{pct('autopay_fail_low')}–{pct('autopay_fail_high')} of Autopay debits failed at big banks", 15, 700, BAD, "middle"))
    s.append(text(776, 416, "Aug 2025, mostly for lack of money", 13, 400, BAD, "middle"))
    return svg(1000, 440, "".join(s))


def p_losses():
    w, x0, x1 = 1000, 40, 960
    X = lambda p: x0 + (x1 - x0) * p / 0.10
    lo, hi, dlo, dhi = n("paytm_ecl_low"), n("paytm_ecl_high"), n("digital_losses_low"), n("digital_losses_high")
    today, be = n("losses_today"), n("be_losses")
    s = [f'<rect x="{x0}" y="70" width="{X(be) - x0}" height="220" fill="{TINT["good"]}"/>',
         f'<rect x="{X(be)}" y="70" width="{x1 - X(be)}" height="220" fill="{TINT["bad"]}"/>',
         text((x0 + X(be)) / 2, 100, "a shopkeeper pays back", 17, 700, GOOD, "middle"),
         text((X(be) + x1) / 2, 100, "we lose money", 17, 700, BAD, "middle"),
         f'<line x1="{x0}" y1="190" x2="{x1}" y2="190" stroke="{MUTED}" stroke-width="1.5"/>']
    for p in range(11):
        s.append(f'<line x1="{X(p / 100)}" y1="184" x2="{X(p / 100)}" y2="196" stroke="{MUTED}"/>')
        s.append(text(X(p / 100), 232, f"{p}%", 14, 400, MUTED, "middle"))
    s.append(f'<rect x="{X(lo)}" y="172" width="{X(hi) - X(lo)}" height="36" rx="6" fill="{THEM}"/>')
    s.append(text((X(lo) + X(hi)) / 2, 148, "Paytm and PhonePe style", 15, 700, THEM, "middle"))
    s.append(text((X(lo) + X(hi)) / 2, 166, f"repaid from the till: {lo * 100:.1f}–{hi * 100:.0f}%", 13, 400, THEM, "middle"))
    s.append(f'<rect x="{X(dlo)}" y="172" width="{X(dhi) - X(dlo)}" height="36" rx="6" fill="{GREY}"/>')
    s.append(text(X(be) + 14, 148, "Lenders who must ask", 15, 700, INK))
    s.append(text(X(be) + 14, 166, f"no till: {dlo * 100:.0f}–{dhi * 100:.0f}% a year", 13, 400, MUTED))
    for p, lab, yy, anchor in ((today, f"Our model assumes {today * 100:.0f}%", 276, "end"), (be, f"Our break-even {be * 100:.1f}%", 276, "start")):
        s.append(f'<line x1="{X(p)}" y1="60" x2="{X(p)}" y2="170" stroke="{US}" stroke-width="3"/>')
        s.append(f'<line x1="{X(p)}" y1="242" x2="{X(p)}" y2="{yy - 16}" stroke="{US}" stroke-width="3"/>')
        s.append(f'<circle cx="{X(p)}" cy="190" r="8" fill="{US}" stroke="#fff" stroke-width="3"/>')
        s.append(text(X(p) + (-10 if anchor == "end" else 10), yy, lab, 16, 700, US, anchor))
    s.append(text(x0, 312, "Bad-loan losses a year, as a share of the money lent", 13, 400, MUTED))
    return svg(w, 320, "".join(s))


def p_lending_and_copying():
    vals = [n("phonepe_ml_fy23"), n("phonepe_ml_fy24"), n("phonepe_ml_fy25"), n("phonepe_ml_h1fy26")]
    s = [f'<rect x="0" y="0" width="520" height="420" rx="16" fill="{PAPER}"/>',
         icon("bank", 20, 18, 40, THEM), text(72, 38, "Already lending", 20, 700), text(72, 58, "PhonePe shop loans given out, ₹ crore", 12.5, 400, MUTED),
         f'<g transform="translate(15,80)">{bars(vals, ["FY23", "FY24", "FY25", "Apr–Sep|2025 only"], [rs(v) for v in vals], [THEM] * 4, 490, 290, hatch_last=True)}</g>',
         text(260, 400, f"Half a year of 2025 was {n('phonepe_ml_h1_x'):.1f}× the same half a year earlier", 13.5, 600, INK, "middle"),
         f'<rect x="545" y="0" width="455" height="420" rx="16" fill="{PAPER}"/>',
         icon("jar", 565, 18, 40, THEM), text(617, 38, "Already copying savings", 20, 700), text(617, 58, "products aimed at our customer", 12.5, 400, MUTED)]
    events = [("2022", "BharatPe sells deposits", "to 80 lakh+ shops", False),
              ("Oct 2024", "PhonePe daily gold", "from ₹10 a day, with Jar", False),
              ("6 Aug 2026", "PhonePe daily deposit", "from ₹100 a day: our shape", True)]
    s.append(f'<line x1="600" y1="110" x2="600" y2="350" stroke="{GREY}" stroke-width="3"/>')
    for i, (when, what, sub, hl) in enumerate(events):
        y = 120 + i * 112
        s.append(f'<circle cx="600" cy="{y}" r="{11 if hl else 8}" fill="{THEM if hl else GREY}" stroke="#fff" stroke-width="3"/>')
        s.append(text(625, y - 6, when, 14, 700, THEM if hl else MUTED))
        s.append(text(625, y + 18, what, 18, 700))
        s.append(text(625, y + 40, sub, 14, 400, MUTED))
    return svg(1000, 420, "".join(s))


def p_four_numbers():
    tiles = [
        ("coin", "Cost to win a shop", f"≤ {rs(n('be_cost'))}", f"today {rs(n('cost_today'))}", "They spend up to|~₹5,000 per device", "warn", "Unknown"),
        ("hands", "Savers who borrow", f"≥ {pct('be_takeup')}", f"today {pct('takeup_today')}", "Their best shops|already have loans", "bad", "Pushed down"),
        ("pct", "Interest rate", f"≥ {pct('be_rate', 1)}", f"today {pct('rate_today')}", "Market prices run|~15% to 30%+", "good", "Safe"),
        ("broken", "Losses", f"≤ {pct('be_losses', 1)}", f"today {pct('losses_today')}", f"They run {pct('paytm_ecl_low', 1)}–{pct('paytm_ecl_high', 0)};|no-till lenders {pct('digital_losses_low')}–{pct('digital_losses_high')}", "bad", "Main risk"),
    ]
    s = []
    for i, (ic, name, line, today, them, kind, verdict) in enumerate(tiles):
        x = i * 252
        s.append(f'<rect x="{x}" y="0" width="234" height="400" rx="16" fill="{PAPER}"/>')
        s.append(f'<rect x="{x}" y="0" width="234" height="8" rx="4" fill="{COL[kind]}"/>')
        s.append(icon(ic, x + 87, 28, 60, US))
        s.append(text(x + 117, 122, name, 17, 700, INK, "middle"))
        s.append(text(x + 117, 150, "WE NEED", 11.5, 700, MUTED, "middle"))
        s.append(text(x + 117, 192, line, 36, 800, US, "middle"))
        s.append(text(x + 117, 216, today, 14, 400, MUTED, "middle"))
        s.append(f'<line x1="{x + 30}" y1="240" x2="{x + 204}" y2="240" stroke="{RULE}" stroke-width="1.5"/>')
        s.append(text(x + 117, 266, "THEY SHOW", 11.5, 700, MUTED, "middle"))
        s.append(text(x + 117, 292, them, 14.5, 600, THEM, "middle", 19))
        s.append(badge(x + 117, 368, kind, verdict, 17))
    return svg(1000, 400, "".join(s))


def p_what_next():
    s = []
    s.append(node(0, 20, 210, 64, "person", INK, "A borrower|we want"))
    s.append(arrow(212, 52, 262, 52))
    s.append(diamond(345, 52, 166, 100, "Can we be paid|before they are?"))
    s.append(arrow(428, 52, 478, 52, GOOD, 2.5))
    s.append(text(440, 42, "Yes", 13, 700, GOOD))
    s.append(node(480, 10, 280, 84, "bank", GOOD, "Salaried, via employer", "salary deduction|is our till", GOOD))
    s.append(f'<rect x="780" y="10" width="220" height="84" rx="12" fill="{TINT["good"]}"/>')
    s.append(text(890, 42, f"+{rs(n('sal_safe_24'))} a customer", 17, 800, GOOD, "middle"))
    s.append(text(890, 64, f"at low losses (3%);|{rs(n('sal_normal_24')).replace('₹-', '−₹')} at normal 6%", 12.5, 400, GOOD, "middle", 15))
    s.append(arrow(345, 102, 345, 160, BAD, 2.5))
    s.append(text(355, 136, "No: shopkeepers", 13, 700, BAD))
    s.append(diamond(345, 215, 210, 100, "Will they share their|whole bank statement?"))
    s.append(arrow(450, 215, 478, 215, GOOD, 2.5))
    s.append(text(452, 205, "Yes", 13, 700, GOOD))
    s.append(node(480, 172, 280, 86, "doc", WARN, "We see every QR's money", "and savings can secure|part of the loan", WARN))
    s.append(f'<rect x="780" y="172" width="220" height="86" rx="12" fill="{TINT["warn"]}"/>')
    s.append(text(890, 205, f"{rs(n('save_year'))} saved", 17, 800, WARN, "middle"))
    s.append(text(890, 227, f"a year at ₹100/day = {pct('save_year_share_of_loan')}|of a ₹1.5 lakh loan", 12.5, 400, WARN, "middle", 15))
    s.append(arrow(345, 265, 345, 318, BAD, 2.5))
    s.append(text(355, 298, "No", 13, 700, BAD))
    s.append(node(200, 320, 290, 80, "phone", BAD, "Partner inside their app", "cheap reach, but they|keep the lending", BAD))
    # the pilot
    s.append(f'<rect x="0" y="420" width="1000" height="118" rx="16" fill="{PAPER}"/>')
    s.append(text(20, 448, "THE PILOT MUST ANSWER", 13, 700, US))
    qs = [("hands", "Do our savers already|have their loan?"), ("doc", "Will they share their|bank statement?"),
          ("jar", "Do Autopay loan|instalments succeed?"), ("phone", "Do they keep saving|vs PhonePe ₹100/day?")]
    for i, (ic, q) in enumerate(qs):
        x = 20 + i * 245
        s.append(f'<circle cx="{x + 22}" cy="{490}" r="20" fill="{US}"/>' + text(x + 22, 496, str(i + 1), 17, 800, "#fff", "middle"))
        s.append(text(x + 52, 484, q, 14.5, 600, INK, lh=18))
    return svg(1000, 545, "".join(s))


def money(k):
    v = n(k)
    sign = "−" if v < 0 else "+"
    return f"{sign}₹{abs(v):,.0f}"


def p_self_select():
    """Bachatt's opt-in filter, and the three loss rates already in the shopkeeper model."""
    s = [f'<rect x="0" y="0" width="468" height="430" rx="16" fill="{PAPER}"/>',
         text(24, 34, "WHO BACHATT ACTUALLY GETS", 13, 700, THEM)]
    s.append(f'<rect x="24" y="52" width="420" height="78" rx="12" fill="#fff" stroke="{RULE}"/>')
    s.append(text(40, 86, f"{n('bachatt_users') / 1e6:.0f} million", 28, 800, THEM))
    s.append(text(230, 80, "signed up", 16, 700))
    s.append(text(230, 104, "since May 2025 · their claim", 13, 400, MUTED))
    s.append(arrow(234, 134, 234, 158, MUTED, 2))
    s.append(text(250, 154, f"about {pct('bachatt_saver_share')} keep a daily debit", 13, 700, MUTED))
    s.append(f'<rect x="24" y="168" width="210" height="92" rx="12" fill="#fff" stroke="{US}" stroke-width="2.5"/>')
    s.append(text(40, 206, f"{n('bachatt_daily_savers') / 1e5:.0f} lakh", 30, 800, US))
    s.append(text(40, 234, "still saving daily", 14, 700))
    s.append(text(250, 196, "our estimate", 15, 700))
    s.append(text(250, 220, "2 million fund purchases", 13.5, 400, MUTED))
    s.append(text(250, 240, "÷ about 20 a month", 13.5, 400, MUTED))
    s.append(arrow(129, 264, 129, 292, MUTED, 2))
    s.append(f'<rect x="24" y="300" width="420" height="106" rx="12" fill="#fff" stroke="{RULE}"/>')
    s.append(icon("bank", 40, 322, 46, THEM))
    s.append(text(100, 340, "The partner books the loan", 16, 700))
    s.append(text(100, 364, f"Up to ₹{n('bachatt_loan_cap') / 1e5:.0f} lakh. Bachatt does not.", 14, 400, MUTED))
    s.append(badge(100, 396, "warn", "The 7–10% loss is not theirs", 13, "start"))

    s.append(f'<rect x="492" y="0" width="508" height="430" rx="16" fill="{PAPER}"/>')
    s.append(text(516, 34, "IF THAT SAVER BORROWS FROM US", 13, 700, US))
    s.append(text(516, 56, "One shopkeeper. Only the loss rate moves.", 13.5, 400, MUTED))
    zero, scale = 790, 170 / max(abs(n("value_if_losses_3")), abs(n("value_if_losses_10")))
    rows = [
        ("value_if_losses_3", "3% losses", "the hope: savers really are safer", GOOD),
        ("value_today", "6% losses", "what the model assumes today", US),
        ("value_if_losses_10", "10% losses", "no till, and no safer than app lenders", BAD),
    ]
    for i, (k, lab, sub, c) in enumerate(rows):
        y = 96 + i * 104
        v = n(k)
        s.append(text(516, y + 6, lab, 18, 700))
        s.append(text(516, y + 28, sub, 13.5, 400, MUTED))
        s.append(text(976, y + 8, money(k), 20, 800, c, "end"))
        bw = abs(v) * scale
        by = y + 46
        if v >= 0:
            s.append(f'<rect x="{zero}" y="{by}" width="{bw}" height="22" rx="4" fill="{c}"/>')
        else:
            s.append(f'<rect x="{zero - bw}" y="{by}" width="{bw}" height="22" rx="4" fill="{c}"/>')
    s.append(f'<line x1="{zero}" y1="138" x2="{zero}" y2="400" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="3 4"/>')
    s.append(text(zero, 418, "₹0", 12, 600, MUTED, "middle"))
    return svg(1000, 430, "".join(s))


def sources():
    rows = sorted(EV, key=lambda r: int(r["id"].split("-")[1]))
    check = {"primary": "opened: company/regulator", "news": "opened: news report", "search summary": "search summary only", "earlier": "earlier research"}
    half = (len(rows) + 1) // 2
    cols = []
    for part in (rows[:half], rows[half:]):
        trs = "".join(f'<tr><td class="id">{r["id"]}</td><td>{html.escape(r["source"])} <span class="d">{html.escape(r["date"])}</span></td><td class="ck">{check[r["status"]]}</td></tr>' for r in part)
        cols.append(f'<table>{trs}</table>')
    return "".join(f'<div>{c}</div>' for c in cols)


def slide(no, kicker, title, visual, caption, src):
    return (f'<section class="slide"><div class="kick"><span class="pg">{no} / {TOTAL}</span>{kicker}</div>'
            f'<h1>{title}</h1><div class="vis">{visual}</div>'
            f'<div class="cap">{caption}</div><div class="src">Sources: {src}</div></section>')


CSS = """
@page { size: A4 landscape; margin: 0; }
* { box-sizing: border-box; }
html, body { margin: 0; background: #fff; }
body { font-family: -apple-system, "Helvetica Neue", Arial, sans-serif; color: INK; }
.slide { width: 297mm; height: 210mm; padding: 13mm 15mm 10mm; display: flex; flex-direction: column; break-after: page; overflow: hidden; position: relative; }
.kick { font-size: 10.5pt; color: MUTED; letter-spacing: .06em; text-transform: uppercase; margin-bottom: 4px; }
.pg { display: inline-block; background: INK; color: #fff; border-radius: 999px; padding: 1px 9px; margin-right: 10px; font-weight: 700; letter-spacing: 0; }
h1 { font-size: 24pt; line-height: 1.15; margin: 2px 0 12px; letter-spacing: -.01em; max-width: 245mm; }
.vis { flex: 1; display: flex; align-items: center; justify-content: center; min-height: 0; }
.vis svg { max-height: 100%; }
.cap { font-size: 13.5pt; font-weight: 600; border-left: 5px solid US; padding: 2px 0 2px 12px; margin-top: 8px; }
.src { font-size: 8.5pt; color: MUTED; margin-top: 6px; }
.cover h1 { font-size: 30pt; }
.srcs { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 8.3pt; }
.srcs table { width: 100%; border-collapse: collapse; }
.srcs td { border-top: 1px solid RULE; padding: 3px 4px; vertical-align: top; line-height: 1.25; }
.srcs .id { color: MUTED; white-space: nowrap; }
.srcs .d { color: MUTED; }
.srcs .ck { color: MUTED; white-space: nowrap; }
"""


def build():
    css = CSS.replace("INK", INK).replace("MUTED", MUTED).replace("RULE", RULE).replace("US", US)
    pages = [
        slide(1, "Can a newcomer win the shopkeepers Paytm and PhonePe already serve?",
              "Half yes: anyone can copy a QR code. Nobody can easily copy the till.",
              p_answer(), "We planned to make our money from lending, and lending is protected by the till, not by the QR.",
              "QM-01, 02, 07, 22, 33"),
        slide(2, "Layer 1 · the QR code", "A QR code protects no one: shops already carry about nine.",
              p_qr(), "Getting onto the counter is easy. What a QR leads to is the real question.",
              "QM-01, 02 (codes and shops, PIB); QM-03, 04 (BharatPe)"),
        slide(3, "Layer 2 · a live test", "When Paytm was hit in 2024, customers left, shops stayed, and loans halved.",
              p_shock(), "The app is easy to leave. The box on the counter and the daily payout are not.",
              "QM-06 to 09 (devices), QM-15, 16 (UPI share), QM-17, 18 (loans)"),
        slide(4, "Layer 3 · the till", "The real moat: Paytm and PhonePe get paid before the shop does.",
              p_paid_first(), "We would always be paid after the shopkeeper, and only if money is left.",
              "QM-19, 20 (repayment from daily payout), QM-26 (Autopay failures)"),
        slide(5, "What the till is worth", "The till keeps their losses below our break-even.",
              p_losses(), "Without the till, we land where other lenders do: at or past our line.",
              "QM-22 (Paytm-sourced loans), QM-40 (digital lenders); our line: deck model, tables/lend_breakeven.csv"),
        slide(6, "They are not standing still", "They already lend to shops at scale, and they are copying savings.",
              p_lending_and_copying(), "Savings can open the door, but it is not an edge they cannot copy.",
              "QM-27 to 30 (PhonePe loans), QM-33, 34 (PhonePe savings), QM-35 (BharatPe)"),
        slide(7, "Our four numbers, for one shopkeeper", "For shopkeepers, take-up and losses move the wrong way. Only the rate is safe.",
              p_four_numbers(), "The QR barely touches our numbers. Losses decide it.",
              "QM-13, 22, 23, 39, 40; our lines: deck model, tables/lend_breakeven.csv"),
        slide(8, "How Bachatt lives without the till",
              "Bachatt does not beat the till. The shopkeeper opts in, and a partner holds the loss.",
              p_self_select(),
              "Choosing to save picks who shows up. It does not, by itself, pick who repays. The +₹597 exists only if savers really are safer, which neither we nor Bachatt have shown.",
              "QM-41 to 45 (Bachatt: users, February purchases, our 20-debit estimate, partner loan, funds raised); shopkeeper values: tables/lend_breakeven.csv, loss rate only; QM-40"),
        slide(9, "What to do", "Start where we are paid first, and let the pilot prove the rest.",
              p_what_next(), "The idea survives the moat only where we sit on the income, or see all of it.",
              "QM-24, 25 (Account Aggregator), QM-33; salaried values: tables/lend_salaried.csv"),
        '<section class="slide"><div class="kick">Sources</div><h1 style="font-size:18pt">Where every number comes from</h1>'
        f'<div class="srcs">{sources()}</div>'
        '<div class="src" style="margin-top:8px">"Search summary only" = seen in a search engine\'s summary, page not opened: treat as reported. '
        'Full claims for each id: QR_moat_test.pdf (sources page) and research/qr_moat.csv. Derived numbers: tables/qr_moat_numbers.csv.</div></section>',
    ]
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>QR moat story</title><style>{css}</style></head><body>{"".join(pages)}</body></html>'


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    src = OUT_DIR / "qr_moat_visual.html"
    src.write_text(build())
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={PDF}", src.as_uri()],
                   check=True, capture_output=True)
    print(f"wrote {src}\nwrote {PDF}")


if __name__ == "__main__":
    main()

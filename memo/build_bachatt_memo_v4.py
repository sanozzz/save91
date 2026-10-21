"""Co-founder memo v4 to Piyush: pictorial; online-first with a ~20% offline TEST arm (operator 19 Oct: "I am not
proposing offline... mostly online + 20% offline... offline we try and figure out") -- offline is never "our wedge". Built on the operator's Bachatt Model slide (19 Oct 2026).
Operator: "In the memo also define the pdf slide that I have the bachatt model. That slide defines Bachatt now which
makes the entry clear and future contested." Then: "build it more pictorial, less text more diagrams, flowchart etc".
Pages: 1 the slide + thesis flow + channel mix; 2 entry = ground floor / contested floors + value per user; 3 credit
staircase + what the offline test arm tests; 4 challenger slide + 6-month pilot; 5 rules map + decisions + sources.
Every number cites a research row ID; "our estimate" / "to verify" where not sourced."""
import math
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
NAVY, INK, MUTED, RULE, PAPER = "#1e3a5f", "#1f2328", "#6b7280", "#e5e7eb", "#f7f8fa"
ACQ, RET, SER = "#2563eb", "#7c3aed", "#059669"
GREEN, RED, AMBER, BLUE = "#15803d", "#b91c1c", "#b45309", "#1f64a8"
LGREEN, LRED, LAMBER, LBLUE = "#e7f5ec", "#fdeceb", "#fff4e0", "#e8f0f9"
PER_USER = 50e7 / 3_000_000        # BAC-04 / BAC-02
AVG_BAL = 350 * 20 * 12 / 2        # illustrative committed saver (our estimate)


def inr(x, d=0):
    w, _, frac = f"{abs(x):.{d}f}".partition(".")
    if len(w) > 3:
        head, tail = w[:-3], w[-3:]
        w = ",".join([head[max(0, i - 2):i] for i in range(len(head), 0, -2)][::-1]) + "," + tail
    return ("−" if x < 0 else "") + "₹" + w + (("." + frac) if frac else "")


def svg(w, h, body):
    return f'<svg viewBox="0 0 {w} {h}" width="100%" font-family="Helvetica, Arial, sans-serif">{body}</svg>'


FS = 1.15   # diagram text scale (operator: more pictorial; keep text legible)


def T(x, y, s, size=12, weight=400, fill=INK, anchor="start"):
    size = round(size * FS, 2)
    return f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{s}</text>'


def box(x, y, w, h, fill, stroke=None, r=10, dash=False):
    st = f' stroke="{stroke}" stroke-width="2"' + (' stroke-dasharray="6 4"' if dash else "") if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{st}/>'


def lines(x, y, txts, size=11.5, weight=400, fill=INK, anchor="middle", lh=None):
    lh = lh or size * 1.3
    return "".join(T(x, y + i * lh, s, size, weight, fill, anchor) for i, s in enumerate(txts))


def arrow(x1, y1, x2, y2, col=MUTED, w=2.5):
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 10 * math.cos(a), y2 - 10 * math.sin(a)
    p1 = (hx - 6 * math.sin(a), hy + 6 * math.cos(a))
    p2 = (hx + 6 * math.sin(a), hy - 6 * math.cos(a))
    return (f'<line x1="{x1}" y1="{y1}" x2="{hx}" y2="{hy}" stroke="{col}" stroke-width="{w}"/>'
            f'<polygon points="{x2},{y2} {p1[0]:.1f},{p1[1]:.1f} {p2[0]:.1f},{p2[1]:.1f}" fill="{col}"/>')


# ---------- the slide ----------
BACHATT = {
    "ACQUISITION": (ACQ, [("✓", "Savings product through debt funds", "stake"), ("✓", "Online acquisition", "stake"),
                          ("✗", "Offline acquisition", "test"), ("✓", "Low-ticket entry (~₹250)", "stake"),
                          ("✓", "→ Digital loans through DSA", "stake")]),
    "RETENTION": (RET, [("✓", "Financial products (MF, Insta Fund, Gold/Silver)", "stake"),
                        ("✗", "Wallet-like: save in / withdraw out", "contest"),
                        ("✓", "Daily / flexible SIP for irregular incomes", "stake"), ("✓", "No lock-in, instant withdraw", "stake")]),
    "SERVICING": (SER, [("✗", "① AI financial planning", "contest"), ("✓", "② Lean DSA + digital", "stake"),
                        ("✓", "③ Loans on book*", "contest"), ("✗", "④ 3-month EMI + gold loan", "contest")]),
}
CHALLENGER = {
    "ACQUISITION": (ACQ, [("✓", "Debt-fund savings (match)", "stake"), ("✓", "Online-first: app + UPI daily SIP", "stake"),
                          ("✓", "~20% offline agents, 1 city", "test"), ("✓", "Loans: partner → risk-share → own book", "contest")]),
    "RETENTION": (RET, [("✓", "Same fund shelf (no digital gold)", "stake"), ("✓", "Habit: app nudges; agent visits", "test"),
                        ("✓", "Save in / out on fund rails", "contest"), ("✓", "Never hold money", "stake")]),
    "SERVICING": (SER, [("✓", "Lean DSA + digital (match)", "stake"), ("✓", "AI planning in the app", "contest"),
                        ("✓", "Credit from the savings record", "edge"), ("✓", "Gold loans: doorstep appraisal", "test")]),
}
TAG = {"stake": ("TABLE STAKES", LGREEN, GREEN), "contest": ("CONTESTED", LRED, RED),
       "test": ("OFFLINE TEST", LAMBER, AMBER), "edge": ("OUR EDGE", LBLUE, BLUE)}


def slide(data=BACHATT, annotate=False, title="Bachatt Model", sub="Acquisition + Retention + Servicing",
          footer="Vision → go-to financial planning app / wallet (save in, withdraw out, finance purchases)",
          footer2="Power move: own the customer relationship + money flows → EMI on products deepens habit and data"):
    cols = []
    for name, (col, items) in data.items():
        rows = ""
        for mark, txt, kind in items:
            mc = GREEN if mark == "✓" else RED
            tag = ""
            if annotate:
                lab, bg, fg = TAG[kind]
                tag = f'<span class="stag" style="background:{bg};color:{fg}">{lab}</span>'
            rows += f'<div class="srow"><span class="smark" style="color:{mc}">{mark}</span><span class="stxt">{txt}</span>{tag}</div>'
        cols.append(f'<div class="scol"><div class="shead" style="background:{col}">{name}</div>{rows}</div>')
    legend = '<div class="slegend"><span style="color:#15803d">✓ Built / live</span><br><span style="color:#b91c1c">✗ Vision / not built</span></div>'
    return (f'<div class="slide"><div class="stop"><div><div class="stitle">{title}</div><div class="ssub">{sub}</div></div>{legend}</div>'
            f'<div class="scols">{"".join(cols)}</div><div class="sfoot"><b>{footer}</b><br><span>{footer2}</span></div></div>')


# ---------- page 1: thesis flow ----------
def thesis():
    s = []
    nodes = [(10, LGREEN, GREEN, "✓", "ENTRY IS CLEAR", ["Every ✓ square can be", "copied: table stakes,", "not a moat"]),
             (285, LRED, RED, "✗", "FUTURE IS CONTESTED", ["Wallet, AI, EMI, gold loans,", "loans on book: where", "the value is won"]),
             (560, LBLUE, BLUE, "★", "OUR ENTRY", ["Online-first to match;", "~20% offline to test", "the contested squares"])]
    for x, bg, fg, ic, head, sub in nodes:
        s.append(box(x, 10, 250, 120, bg, fg))
        s.append(T(x + 22, 52, ic, 30, 800, fg))
        s.append(T(x + 62, 46, head, 13.5, 800, fg))
        s.append(lines(x + 62, 70, sub, 11, 500, INK, "start", 15))
    s.append(arrow(262, 70, 283, 70, INK))
    s.append(arrow(537, 70, 558, 70, INK))
    return svg(820, 140, "".join(s))


def mix():
    s = [T(0, 16, "HOW WE'D ENTER: ONLINE-FIRST, WITH OFFLINE AS A TEST", 12, 800, NAVY)]
    split = 10 + 0.8 * 800
    s.append(f'<rect x="10" y="32" width="{split - 10}" height="64" rx="10" fill="{ACQ}"/>')
    s.append(f'<rect x="{split + 4}" y="32" width="{806 - split}" height="64" rx="10" fill="{AMBER}"/>')
    s.append(T(28, 58, "ONLINE CORE · ~80% of savers", 13.5, 800, "#fff"))
    s.append(T(28, 82, "App + UPI daily SIP + digital loans: matches every ✓ square", 10.5, 500, "#fff"))
    s.append(lines((split + 810) / 2, 58, ["OFFLINE TEST", "~20% of savers"], 11, 800, "#fff", "middle", 20))
    s.append(arrow(330, 98, 330, 122, ACQ, 2.5))
    s.append(arrow((split + 810) / 2, 98, (split + 810) / 2, 122, AMBER, 2.5))
    s.append(box(10, 124, 390, 78, LBLUE, ACQ))
    s.append(T(26, 148, "ONLINE: match, then out-credit", 12.5, 800, ACQ))
    s.append(lines(26, 170, ["Parity with Bachatt's ✓ squares in 6–9 months", "Edge: credit from the daily savings record"], 10.5, 500, INK, "start", 16))
    s.append(box(420, 124, 390, 78, LAMBER, AMBER))
    s.append(T(436, 148, "OFFLINE: try it and find out", 12.5, 800, AMBER))
    s.append(lines(436, 170, ["Does a person lift retention, reach, gold loans?", "Month 6: grow, hold or drop the arm"], 10.5, 500, INK, "start", 16))
    return svg(820, 210, "".join(s))


# ---------- page 2: ground floor vs contested floors ----------
def building():
    s = []
    # contested floor (top)
    s.append(box(40, 10, 740, 120, "#fff", RED, 12, dash=True))
    s.append(T(56, 34, "THE CONTESTED FLOORS: value is won here", 12.5, 800, RED))
    up = ["Offline acquisition", "Wallet: save in / out", "AI financial planning", "3-month EMI + gold loan", "Loans on book*"]
    for i, u in enumerate(up):
        x = 56 + i * 145
        s.append(box(x, 48, 135, 66, LRED))
        s.append(T(x + 10, 70, "✗", 16, 800, RED))
        words = u.split(" ")
        l1, l2 = [], []
        for w in words:
            (l1 if len(" ".join(l1 + [w])) <= 16 else l2).append(w)
        s.append(lines(x + 30, 72, [" ".join(l1), " ".join(l2)], 10.5, 700, INK, "start", 14))
    # ground floor
    s.append(box(40, 150, 740, 150, "#fff", GREEN, 12))
    s.append(T(56, 174, "THE GROUND FLOOR: Bachatt's ✓ squares, which anyone can build", 12.5, 800, GREEN))
    blocks = [("Debt-fund savings", "ARN ₹40k (REG-036)"), ("Online acquisition", "≈₹500 per saver*"),
              ("Low ticket, daily SIP", "UPI auto-debit"), ("Fund shelf", "MF, Insta, gold funds"),
              ("Instant withdraw", "≤ ₹50k a day (REG-041)"), ("DSA loans", "1–3% fee (XL-13)")]
    for i, (h, c) in enumerate(blocks):
        x = 56 + i * 121
        s.append(box(x, 188, 113, 96, LGREEN))
        s.append(T(x + 8, 208, "✓", 15, 800, GREEN))
        words = h.split(" ")
        l1, l2 = [], []
        for w in words:
            (l1 if len(" ".join(l1 + [w])) <= 13 else l2).append(w)
        s.append(lines(x + 8, 230, [" ".join(l1), " ".join(l2)], 10.5, 700, INK, "start", 13))
        s.append(box(x + 6, 258, 101, 20, "#fff", None, 6))
        s.append(T(x + 56, 272, c, 8.6, 600, GREEN, "middle"))
    s.append(box(560, 316, 220, 34, NAVY, None, 17))
    s.append(T(670, 338, "≈ 6–9 months to match", 12.5, 800, "#fff", "middle"))
    s.append(T(40, 338, "* online cost per activated saver is our estimate; Bachatt's 'loans on book' is unverified (XL-12)", 9.5, 400, MUTED))
    return svg(820, 360, "".join(s))


def value():
    rows = [("Bachatt: trail on ~" + inr(PER_USER) + " per user", PER_USER * 0.0035, "a year", NAVY),
            ("Committed ₹350-a-day saver", AVG_BAL * 0.0035, "a year", NAVY),
            ("One personal loan via DSA", 58522 * 0.02, "once", AMBER),
            ("Same loan, we share the risk", 58522 * 0.0475, "once", AMBER)]
    x0, x1, top, gap = 290, 740, 34, 38
    lo, hi = math.log10(0.1), math.log10(10000)
    X = lambda v: x0 + (x1 - x0) * (math.log10(max(v, .1)) - lo) / (hi - lo)
    s = [T(0, 16, "WHY THE UPPER FLOORS MATTER: WHAT ONE USER IS WORTH (₹, LOG SCALE)", 12, 800, NAVY)]
    for v in (1, 10, 100, 1000, 10000):
        s.append(f'<line x1="{X(v)}" y1="{top - 6}" x2="{X(v)}" y2="{top + gap * 4 - 8}" stroke="{RULE}"/>' + T(X(v), top + gap * 4 + 6, inr(v), 10, 400, MUTED, "middle"))
    for i, (lab, v, per, col) in enumerate(rows):
        y = top + i * gap
        s.append(T(0, y + 17, lab, 11.5, 700))
        s.append(box(x0, y + 3, max(X(v) - x0, 3), 22, col, None, 4))
        s.append(T(X(v) + 6, y + 19, f"{inr(v, 1 if v < 10 else 0)} {per}", 12.5, 800, col))
    s.append(T(0, top + gap * 4 + 26, "Sources: BAC-02/04, XB-04 (trail 0.2–0.5%), XL-13, XL-29 (₹58,522 average loan), SE-05/XB-07 (4.5–5%). The ₹350-a-day saver is our illustration.", 9, 400, MUTED))
    return svg(820, top + gap * 4 + 34, "".join(s))


# ---------- page 3: credit staircase + wedge flowchart ----------
def staircase():
    steps = [("DSA fee", "1–3% once", "XL-13", 1), ("Marketplace", "≤ 4.6%", "XL-09", 2),
             ("Share the risk", "4.5–5%", "SE-05", 3), ("LSP with first-loss", "~8–9% net", "LEV-061", 4),
             ("Own NBFC", "21% NIM − 8–10% losses − 9% opex ≈ 1% RoMA", "LEV-026", 5)]
    s = [T(0, 16, "THE CREDIT STAIRCASE: EACH STEP EARNS MORE, AND CARRIES MORE RISK", 12, 800, NAVY)]
    w = 150
    for i, (h, v, src, k) in enumerate(steps):
        x = 10 + i * (w + 8)
        y = 220 - k * 36
        col = AMBER if k <= 3 else (BLUE if k == 4 else RED)
        s.append(box(x, y, w, 250 - y, col, None, 6))
        s.append(T(x + w / 2, y + 22, h, 11.5, 800, "#fff", "middle"))
        if k < 5:
            s.append(T(x + w / 2, y + 42, v, 13, 800, "#fff", "middle"))
        else:
            s.append(lines(x + w / 2, y + 42, ["21% NIM", "− 8–10% losses", "− 9% opex", "≈ 1% return"], 11, 700, "#fff", "middle", 15))
        s.append(T(x + w / 2, 244, src, 9, 600, "#fff", "middle"))
    s.append(arrow(30, 266, 780, 266, INK, 2))
    s.append(T(30, 284, "more risk, more capital, more data needed →", 10.5, 600, MUTED))
    s.append(T(780, 284, "the edge = credit quality from the savings record", 10.5, 800, NAVY, "end"))
    return svg(820, 292, "".join(s))


def test_arm():
    s = [T(0, 16, "WHAT THE ~20% OFFLINE ARM TESTS: CAN A PERSON UNLOCK THE CONTESTED SQUARES?", 12, 800, NAVY)]
    cx, cy = 410, 175
    s.append(f'<circle cx="{cx}" cy="{cy}" r="72" fill="{LAMBER}" stroke="{AMBER}" stroke-width="3" stroke-dasharray="7 4"/>')
    s.append(lines(cx, cy - 12, ["OFFLINE", "TEST ARM", "(~20%)"], 13, 800, AMBER, "middle", 17))
    outs = [(110, 70, "Retention?", "does a visit keep", "the saver saving?", "test: still saving, by arm"),
            (710, 70, "Reach?", "does a visit win savers", "online can't reach?", "test: cost per saver kept"),
            (110, 285, "Gold loans?", "physical gold, checked", "at the door (REG-022/023)", "test: doorstep appraisal"),
            (710, 285, "AI planning?", "does advice become", "action via a person?", "test: products taken")]
    for x, y, h, a, b, c in outs:
        s.append(box(x - 105, y - 38, 210, 84, "#fff", RED, dash=True))
        s.append(T(x, y - 14, h, 13, 800, RED, "middle"))
        s.append(lines(x, y + 6, [a, b, c], 10.5, 500, INK, "middle", 13))
        sx = cx + (60 if x > cx else -60)
        sy = cy + (-40 if y < cy else 40)
        ex = x + (-105 if x > cx else 105)
        ey = y + (12 if y < cy else -12)
        s.append(arrow(sx, sy, ex, ey, AMBER, 3))
    s.append(T(410, 360, "Who else wants these: Paytm/PhonePe (wallet, merchants), Jar (daily savings), Snapmint/Bajaj (EMI), Muthoot/Manappuram (gold)", 9.5, 500, MUTED, "middle"))
    return svg(820, 370, "".join(s))


# ---------- deeper findings ----------
LOAN = 58522                           # XL-29 average personal loan
CAC = 500                              # our estimate: online cost per activated saver
DSA_FEE, SHARE_FEE, LSP_NET = 0.02, 0.0475, 0.085   # XL-13; SE-05/XB-07; LEV-061 (net of DLG, before own costs)
JAR_ACTIVE = 0.07                      # LEV-040, derived
TRAIL = 0.0035                         # XB-04 mid
DAILY, DAYS = 350, 20                  # illustrative committed saver (IV-03: Rs 200-500 a day)
PIGMY_PAY = 0.025                      # NG-041 cap on agent commission


def findings():
    need_dsa = CAC / (LOAN * DSA_FEE)
    rows = [("₹167", NAVY, LBLUE, "invested per Bachatt user (₹50 Cr ÷ 3M users, company claims)",
             f"At a 0.35% trail that earns {inr(PER_USER * TRAIL, 1)} a year. Savings is the hook; credit is the business.", "BAC-02/04, XB-04"),
            ("36%", RED, LRED, "of SBI's ₹250 daily SIPs started in FY26 had stopped by year-end",
             "Small savers are easy to sign and hard to keep: Chhoti SIPs close ~7 for every 10 opened.", "NG-033, NG-034"),
            (f"{need_dsa:.0%}", AMBER, LAMBER, f"of savers must take a DSA loan just to repay a {inr(CAC)} acquisition",
             "Paytm's merchants sit at ≈5%. Sharing loan risk cuts the bar to 18%; an LSP's to ~10%.",
             "XL-13, XL-29, SE-05, LEV-061, XB-06 (derived); ₹500 per saver is our estimate"),
            ("2% vs 9%", GREEN, LGREEN, "bad loans: SHGs that save before borrowing vs microfinance",
             "Saving may predict repayment, but it's correlational; a US trial found no average effect.", "EVD-03 (2.05% vs 8.72%), EVD-01"),
            ("₹10/day", BLUE, LBLUE, "PhonePe Daily Savings, built with Jar (October 2024)",
             "The UPI giants already sell the ground floor; a challenger wins on depth, not reach.", "SAV-08, JAR-06/07 (Jar: 35M registered, profitable)")]
    s = [T(0, 16, "FIVE NUMBERS THAT SHAPE THE CALL", 12, 800, NAVY)]
    for i, (num, col, bg, head, so, src) in enumerate(rows):
        y = 30 + i * 86
        s.append(box(0, y, 190, 76, bg, col))
        s.append(T(95, y + 48, num, 22 if len(num) > 5 else 26, 800, col, "middle"))
        s.append(T(210, y + 22, head, 13, 800))
        s.append(T(210, y + 45, so, 11, 500))
        s.append(T(210, y + 66, src, 9, 500, MUTED))
    return svg(820, 30 + 5 * 86, "".join(s))


def donut(cx, cy, frac, col, label, r=50):
    c = 2 * math.pi * r
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{RULE}" stroke-width="16"/>'
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="16" '
            f'stroke-dasharray="{frac * c:.1f} {c:.1f}" transform="rotate(-90 {cx} {cy})"/>'
            + T(cx, cy + 8, label, 17, 800, col, "middle"))


def leak():
    s = [T(0, 16, "THE LEAK: SMALL SAVERS ARE EASY TO SIGN, HARD TO KEEP", 12, 800, NAVY)]
    items = [(0.07, RED, "7%", "Jar", "active of registered", "derived, LEV-040"),
             (0.24, RED, "24%", "PhonePe merchants", "active of registered", "NG-038"),
             (0.64, AMBER, "64%", "SBI ₹250 daily SIP", "still running at year-end", "NG-033"),
             (0.71, RED, "71", "Chhoti SIP (₹250)", "closed per 100 opened", "NG-034"),
             (1.0, GREEN, "5+ yrs", "Doorstep collector", "how long most save", "one interview, IV-11")]
    for i, (f, col, lab, a, b, c) in enumerate(items):
        cx = 82 + i * 164
        s.append(donut(cx, 96, f, col, lab))
        s.append(T(cx, 176, a, 11.5, 800, INK, "middle"))
        s.append(T(cx, 193, b, 10, 500, INK, "middle"))
        s.append(T(cx, 208, c, 8.8, 500, MUTED, "middle"))
    # what it implies for Bachatt
    active = 3_000_000 * JAR_ACTIVE
    s.append(box(20, 232, 300, 64, PAPER, NAVY))
    s.append(T(170, 258, "3M users × ₹167", 15, 800, NAVY, "middle"))
    s.append(T(170, 282, "what Bachatt reports", 10, 500, MUTED, "middle"))
    s.append(arrow(326, 264, 486, 264, NAVY, 3))
    s.append(T(406, 254, "if Bachatt looks", 9.5, 700, NAVY, "middle"))
    s.append(T(406, 286, "like Jar (~7% active)", 9.5, 700, NAVY, "middle"))
    s.append(box(492, 232, 310, 64, LBLUE, NAVY))
    s.append(T(647, 258, f"≈{active / 1e5:.0f} lakh savers × ≈{inr(round(50e7 / active, -2))}", 15, 800, NAVY, "middle"))
    s.append(T(647, 282, "a small, deeper core (our read; NG-032: no active count)", 10, 500, MUTED, "middle"))
    return svg(820, 304, "".join(s))


def payback():
    s = [T(0, 16, f"WHO PAYS FOR A {inr(CAC)} SAVER? SHARE OF SAVERS WHO MUST BORROW ONCE TO REPAY IT", 12, 800, NAVY)]
    x0, x1, top, gap = 330, 780, 40, 42
    X = lambda p: x0 + (x1 - x0) * p / 0.5
    rows = [("Via DSA fee", LOAN * DSA_FEE, AMBER), ("We share the risk", LOAN * SHARE_FEE, AMBER),
            ("LSP with first-loss", LOAN * LSP_NET, BLUE)]
    # trail-only row
    s.append(T(0, top + 17, "Savings trail alone", 11.5, 800))
    s.append(T(x0, top + 17, f"{CAC / (AVG_BAL * TRAIL):.1f} years for a committed saver; never at Bachatt's ₹167", 11, 700, MUTED))
    for i, (lab, fee, col) in enumerate(rows, start=1):
        y = top + i * gap
        p = CAC / fee
        s.append(T(0, y + 17, f"{lab} (≈{inr(round(fee, -1))} a loan)", 11.5, 800))
        s.append(box(x0, y + 2, X(p) - x0, 24, col, None, 4))
        s.append(T(X(p) + 6, y + 19, f"{p:.0%}", 13, 800, col))
    xb = X(0.05)
    s.append(f'<line x1="{xb}" y1="{top + gap - 6}" x2="{xb}" y2="{top + gap * 4 - 6}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>')
    s.append(T(xb - 4, top + gap * 4 + 10, "Paytm today ≈5% (XB-06, derived)", 10, 800, RED, "start"))
    s.append(T(0, top + gap * 4 + 30, "And it must happen early: a third of small-ticket savers stop within the year (NG-033). Sources: XL-29, XL-13, SE-05, LEV-061; ₹500 is our estimate.", 9, 400, MUTED))
    return svg(820, top + gap * 4 + 38, "".join(s))


def evidence():
    s = [T(0, 16, "DOES SAVING PREDICT REPAYMENT? THE BET EVERYONE IN THIS SPACE IS MAKING", 12, 800, NAVY)]
    s.append(f'<line x1="70" y1="52" x2="750" y2="52" stroke="{INK}" stroke-width="4"/>')
    s.append(f'<polygon points="410,54 386,92 434,92" fill="{NAVY}"/>')
    s.append(T(410, 86, "?", 16, 800, "#fff", "middle"))
    for x in (205, 615):
        s.append(f'<line x1="{x}" y1="52" x2="{x}" y2="104" stroke="{MUTED}" stroke-width="2"/>')
    left = [["✓ SHGs save first: 2.05% bad loans", "   vs 8.72% for microfinance (EVD-03)"],
            ["✓ App behaviour predicted credit for", "   no-history borrowers, Mexico (EVD-02)"],
            ["✓ Bachatt already underwrites on", "   behaviour data (XB-10)"]]
    right = [["✗ The SHG gap is correlational:", "   the groups differ (EVD-03)"],
             ["✗ US savings-loan trial: no average", "   score effect; 39% paid late (EVD-01)"],
             ["✗ No Indian evidence yet for", "   app savers (EVD-02 note)"]]
    for x0, items, col, bg, head in ((20, left, GREEN, LGREEN, "FOR"), (430, right, RED, LRED, "AGAINST / UNPROVEN")):
        s.append(box(x0, 104, 370, 168, bg, col))
        s.append(T(x0 + 185, 126, head, 12, 800, col, "middle"))
        for j, ln in enumerate(items):
            s.append(lines(x0 + 16, 150 + j * 42, ln, 10.5, 600, INK, "start", 15))
    s.append(box(20, 286, 560, 52, PAPER, None, 8))
    s.append(lines(34, 306, ["Why it matters: 55% of new small-business borrowers are new to credit (NG-042);",
                             "self-employed unsecured loans peak at 10–11% bad (NG-015). A signal that works is worth a lot."], 10, 500, INK, "start", 16))
    s.append(box(596, 286, 206, 52, NAVY, None, 26))
    s.append(lines(699, 307, ["Plausible, not proven:", "the pilot's first test"], 11, 800, "#fff", "middle", 16))
    return svg(820, 346, "".join(s))


def compmap():
    s = [T(0, 16, "WHO ELSE IS HERE: THE ONLINE SAVINGS → CREDIT LANE IS CROWDED", 12, 800, NAVY)]
    quads = [(60, 34, "ONLINE · SAVINGS-LED", ACQ), (435, 34, "ONLINE · CREDIT-LED", ACQ),
             (60, 214, "ASSISTED · SAVINGS-LED", AMBER), (435, 214, "ASSISTED · CREDIT-LED", AMBER)]
    for x, y, lab, col in quads:
        s.append(box(x, y, 365, 172, PAPER, None, 8))
        s.append(T(x + 10, y + 18, lab, 10, 800, col))
    s.append(T(30, 120, "ONLINE", 10, 800, ACQ, "middle").replace("<text", '<text transform="rotate(-90 30 120)"'))
    s.append(T(30, 300, "ASSISTED", 10, 800, AMBER, "middle").replace("<text", '<text transform="rotate(-90 30 300)"'))
    s.append(T(242, 402, "← SAVINGS-LED", 10, 800, MUTED, "middle"))
    s.append(T(617, 402, "CREDIT-LED →", 10, 800, MUTED, "middle"))

    def pill(x, y, a, b, col=INK, bg="#fff", w=160):
        return box(x, y, w, 40, bg, col, 8) + T(x + 10, y + 17, a, 11, 800, col) + T(x + 10, y + 33, b, 9, 500, INK if bg == "#fff" else "#fff")

    s.append(pill(72, 60, "Jar", "35M registered · profitable"))
    s.append(pill(72, 108, "PhonePe / Paytm", "₹10-a-day auto-save"))
    s.append(pill(72, 156, "Bachatt", "3M users · $16M raised"))
    s.append(pill(482, 60, "Moneyview", "LSP + own NBFC"))
    s.append(pill(482, 150, "Kissht", "53M registered"))
    s.append(pill(650, 105, "Paisabazaar", "marketplace ≤ 4.6%", w=140))
    s.append(pill(72, 240, "Pigmy collectors", "daily doorstep, since 1928"))
    s.append(pill(72, 300, "SHGs", "save first · 2% bad loans"))
    s.append(pill(482, 240, "Microfinance", "8.7% bad loans"))
    s.append(pill(482, 300, "PM SVANidhi", "53 lakh vendor loans"))
    s.append(pill(650, 270, "Gold-loan cos", "branch appraisal", w=140))
    s.append(arrow(234, 80, 476, 80, ACQ, 2.5))
    s.append(T(355, 74, "Jar: P2P test (JAR-11)", 9, 700, ACQ, "middle"))
    s.append(arrow(234, 176, 476, 176, ACQ, 2.5))
    s.append(T(412, 170, "Bachatt: partner loans", 9, 700, ACQ, "middle"))
    s.append(box(262, 104, 150, 40, NAVY, None, 8))
    s.append(T(337, 121, "★ Challenger", 11, 800, "#fff", "middle"))
    s.append(T(337, 137, "online-first", 9, 600, "#fff", "middle"))
    s.append(f'<line x1="337" y1="146" x2="337" y2="258" stroke="{AMBER}" stroke-width="2.5" stroke-dasharray="6 4"/>')
    s.append(f'<polygon points="337,266 331,254 343,254" fill="{AMBER}"/>')
    s.append(T(345, 228, "~20% test arm", 9.5, 800, AMBER))
    s.append(T(300, 290, "no app plays", 10, 700, MUTED, "middle"))
    s.append(T(300, 304, "in this lane", 10, 700, MUTED, "middle"))
    return svg(820, 410, "".join(s))


def moves():
    s = [T(0, 16, "IF THEY MOVE, WHAT CHANGES FOR US (OUR READ)", 12, 800, NAVY)]
    ms = [("Bachatt buys an NBFC", "as Amazon Pay and CRED did", "(LEV-030)", "a licence is no edge;", "the credit signal is"),
          ("PhonePe pushes ₹10/day", "already live with Jar", "(SAV-08)", "the ground floor goes free;", "win on depth, not reach"),
          ("Bachatt adds agents", "it has $16M to try", "(QM-45)", "our test arm has to", "learn faster")]
    for i, (h, a, b, c, d) in enumerate(ms):
        x = 4 + i * 274
        s.append(box(x, 30, 262, 52, LRED, RED))
        s.append(T(x + 131, 50, h, 11.5, 800, RED, "middle"))
        s.append(T(x + 131, 70, f"{a} {b}", 9, 500, INK, "middle"))
        s.append(arrow(x + 131, 84, x + 131, 104, INK, 2))
        s.append(box(x, 106, 262, 48, LBLUE, NAVY))
        s.append(lines(x + 131, 125, [c, d], 10.5, 800, NAVY, "middle", 15))
    return svg(820, 160, "".join(s))


def offline_cost():
    s = [T(0, 16, "WHY OFFLINE IS A TEST: A DOORSTEP VISIT COSTS ~14× WHAT THE FUND PAYS", 12, 800, NAVY)]
    pay = DAILY * DAYS * 12 * PIGMY_PAY
    trail = AVG_BAL * TRAIL
    x0, x1 = 300, 640
    X = lambda v: x0 + (x1 - x0) * v / pay
    for i, (lab, sub, v, col) in enumerate([("Pigmy-style agent pay", f"2.5% of {inr(DAILY * DAYS)} collected a month", pay, AMBER),
                                            ("Debt-fund trail", f"on that saver's ~{inr(AVG_BAL)} balance", trail, NAVY)]):
        y = 36 + i * 56
        s.append(T(0, y + 16, lab, 12, 800))
        s.append(T(0, y + 33, sub, 9.5, 500, MUTED))
        s.append(box(x0, y + 2, max(X(v) - x0, 4), 30, col, None, 4))
        s.append(T(max(X(v), x0 + 4) + 8, y + 23, f"{inr(round(v))} a year per saver", 12, 800, col))
    s.append(box(0, 154, 810, 56, LAMBER, AMBER))
    s.append(lines(14, 176, ["A co-op bank can pay its collectors because it LENDS the deposits; a fund distributor earns only the trail.",
                             "So the offline arm must pay its way through credit, or cost far less per visit. That is what the 20% tests."], 10.5, 600, INK, "start", 17))
    s.append(T(0, 232, f"Sources: NG-041 (commission capped at 2.5%, was 3–4%), XB-04. One co-op collector we spoke to: 200–400 savers, ₹200–500 a day,", 9, 400, MUTED))
    s.append(T(0, 246, "most saving 5+ years, salary ₹15–25k + under 2% (IV-01/03/11/13). The ₹350-a-day saver is our illustration.", 9, 400, MUTED))
    return svg(820, 252, "".join(s))


# ---------- page 5: rules map + pilot timeline ----------
def rules():
    s = [T(0, 16, "THE RULES SHAPE THE DESIGN: ALLOWED ✓ AND BLOCKED ✗ MONEY FLOWS", 12, 800, NAVY)]
    s.append(box(10, 40, 150, 70, LBLUE, BLUE))
    s.append(lines(85, 70, ["Saver's own", "bank / UPI"], 12, 800, BLUE, "middle"))
    s.append(box(330, 40, 160, 70, LGREEN, GREEN))
    s.append(lines(410, 70, ["Mutual fund", "(in his name)"], 12, 800, GREEN, "middle"))
    s.append(box(640, 40, 170, 70, LGREEN, GREEN))
    s.append(lines(725, 70, ["Lender books", "the loan"], 12, 800, GREEN, "middle"))
    s.append(arrow(162, 75, 328, 75, GREEN, 3))
    s.append(T(245, 66, "✓ REG-066", 10, 800, GREEN, "middle"))
    s.append(arrow(492, 75, 638, 75, GREEN, 3))
    s.append(T(565, 66, "✓ we source", 10, 800, GREEN, "middle"))
    blocked = [(10, "Our app holds", "customer money", "✗ BUDS Act (REG-081)"),
               (215, "Stored-value", "wallet balance", "✗ needs RBI licence"),
               (420, "Loan against gold", "fund / digital gold", "✗ REG-022/023"),
               (625, "Cash into funds", "> ≈₹50k a year", "✗ legal opinion first")]
    for x, a, b, c in blocked:
        s.append(box(x, 140, 190, 82, LRED, RED))
        s.append(lines(x + 95, 164, [a, b], 11.5, 700, INK, "middle"))
        s.append(T(x + 95, 207, c, 10, 800, RED, "middle"))
    return svg(820, 232, "".join(s))


def pilot():
    s = [T(0, 16, "PROVE IT IN ONE CITY IN 6 MONTHS, THEN RAISE", 12, 800, NAVY)]
    y = 70
    s.append(f'<line x1="70" y1="{y}" x2="750" y2="{y}" stroke="{NAVY}" stroke-width="4"/>')
    ms = [(70, "Month 0", "Launch online;", "test arm in 1 city"), (240, "Month 1–3", "Cost per saver kept,", "online vs offline"),
          (410, "Month 3–6", "Still saving, by arm;", "first small loans"), (580, "Month 4–6", "Savings streak vs", "repayment; lender terms"),
          (750, "Month 6", "Grow, hold or", "drop the test arm")]
    for x, h, a, b in ms:
        s.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{NAVY}"/>')
        s.append(T(x, y - 22, h, 11.5, 800, NAVY, "middle"))
        s.append(lines(x, y + 34, [a, b], 10.5, 500, INK, "middle", 13))
    gates = [("Cost per kept saver", "online vs test arm"), ("Saving at 6 months", "beat ₹250 SIPs' 36% stop"),
             ("Streak → repayment", "does saving predict it?"), ("Credit take-up", "above Paytm's ≈5%"),
             ("Test arm pays back", "via credit, not trail")]
    for i, (a, b) in enumerate(gates):
        x = 10 + i * 162
        s.append(box(x, 132, 154, 64, PAPER, NAVY))
        s.append(T(x + 77, 154, a, 10.5, 800, NAVY, "middle"))
        s.append(T(x + 77, 176, b, 9.3, 500, INK, "middle"))
    return svg(820, 206, "".join(s))



CSS = f"""
@page {{ size: A4; margin: 13mm 12mm; }}
body {{ font-family: Helvetica, Arial, sans-serif; color: {INK}; font-size: 10.3pt; line-height: 1.4; }}
h1 {{ color: {NAVY}; font-size: 19pt; margin: 0 0 2px; }}
h2 {{ color: {NAVY}; font-size: 14pt; margin: 6px 0 6px; }}
.sub {{ color: {MUTED}; font-size: 9.6pt; margin-bottom: 6px; }}
.pb {{ page-break-before: always; }}
.card {{ border: 1px solid #d7dde6; border-radius: 10px; padding: 10px; margin: 8px 0; page-break-inside: avoid; }}
.blk {{ break-inside: avoid; page-break-inside: avoid; }}
.take {{ background: {NAVY}; color: #fff; border-radius: 8px; padding: 7px 12px; font-weight: 700; margin: 6px 0; }}
.rec {{ background: {LGREEN}; border-left: 5px solid {GREEN}; padding: 7px 12px; margin: 8px 0; font-size: 10.5pt; }}
.slide {{ border-radius: 10px; overflow: hidden; border: 1px solid #d7dde6; margin: 6px 0; page-break-inside: avoid; background: {PAPER}; }}
.stop {{ background: {NAVY}; color: #fff; padding: 9px 14px; display: flex; justify-content: space-between; align-items: center; }}
.stitle {{ font-size: 16pt; font-weight: 800; }} .ssub {{ font-size: 9pt; color: #c7d2e0; }}
.slegend {{ background: #fff; border-radius: 8px; padding: 4px 10px; font-size: 8.3pt; font-weight: 700; }}
.scols {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; padding: 9px; }}
.scol {{ background: #fff; border-radius: 6px; padding-bottom: 4px; }}
.shead {{ color: #fff; font-weight: 800; text-align: center; padding: 5px; font-size: 10pt; border-radius: 6px 6px 0 0; }}
.srow {{ padding: 4px 8px; font-size: 9pt; display: flex; gap: 5px; align-items: flex-start; flex-wrap: wrap; }}
.smark {{ font-weight: 800; }} .stxt {{ flex: 1; min-width: 55%; }}
.stag {{ font-size: 6.8pt; font-weight: 800; padding: 1px 5px; border-radius: 6px; white-space: nowrap; }}
.sfoot {{ background: {NAVY}; color: #fff; text-align: center; padding: 7px 10px; font-size: 9.2pt; }} .sfoot span {{ color: #c7d2e0; font-size: 8.3pt; }}
.chips {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 6px; }}
.chip {{ border: 2px solid {NAVY}; border-radius: 10px; padding: 7px 10px; font-weight: 700; color: {NAVY}; font-size: 10pt; }}
table {{ border-collapse: collapse; width: 100%; font-size: 8.8pt; table-layout: fixed; }}
th {{ background: {NAVY}; color: #fff; text-align: left; padding: 4px 6px; }} td {{ border-bottom: 1px solid {RULE}; padding: 4px 6px; vertical-align: top; }}
.small {{ font-size: 8.4pt; color: {MUTED}; }}
"""

P1 = f"""
<h1>Bachatt today: entry is clear, the future is contested</h1>
<div class="sub">Memo for Piyush · From Sandeep · 19 October 2026 · Should we launch a challenger, and where do we fight?</div>
{slide()}
<div class="small">* Bachatt's site says partner NBFCs disburse its loans (XL-12), so "loans on book" needs verifying.</div>
<div class="card">{thesis()}</div>
<div class="card">{mix()}</div>
<div class="rec"><b>Recommendation:</b> launch <b>online-first</b> and match the ✓ squares in 6–9 months. Compete where Bachatt is thin:
<b>committed savers in one segment</b>, and <b>credit priced from their savings record</b>. Run <b>~20% offline</b> as a test arm; 6 months of data decide whether it grows.</div>
"""

P2 = f"""
<div class="pb"></div>
<div class="blk"><h2>What we found, in five numbers</h2>
<div class="card">{findings()}</div>
<div class="take">The race is not to sign the most savers. It is to keep committed savers, and to prove their saving predicts repayment before anyone else does.</div></div>
"""

P3 = f"""
<div class="blk"><h2>1 · Entry is clear: anyone can build the ground floor</h2>
<div class="card">{building()}</div>
<div class="take">Copying Bachatt's ✓ squares gets us parity at best. The market will be won on the contested floors.</div></div>
<div class="blk"><div class="card">{value()}</div>
<div class="take">Savings trail is under ₹1 a user a year at Bachatt's visible balances (~{inr(PER_USER)} a user). One loan is worth more than years of trail.</div></div>
"""

P4 = f"""
<div class="blk"><h2>2 · Savings is the hook, not the business</h2>
<div class="card">{leak()}</div>
<div class="take">Small-ticket savers leave apps and SIPs fast; the one doorstep collector we spoke to keeps most for 5+ years. Bachatt's 3M is sign-ups: it publishes no active count.</div></div>
<div class="blk"><div class="card">{payback()}</div>
<div class="take">Savings can't repay what a saver costs to win. Whoever wins has to climb the credit ladder, with savers who stay long enough to borrow.</div></div>
"""

P5 = f"""
<div class="blk"><h2>3 · The money is in credit; the edge is the signal</h2>
<div class="card">{staircase()}</div>
<div class="take">A licence alone doesn't make an NBFC profitable: fintech NBFCs keep about 1% after losses. Credit quality decides it.</div></div>
<div class="blk"><div class="card">{evidence()}</div>
<div class="take">If saving predicts repayment, the player with deeper savers wins on credit. If it doesn't, this is a thin-fee lead business. Test it first.</div></div>
"""

P6 = f"""
<div class="blk"><h2>4 · Who else is here, and what they might do</h2>
<div class="card">{compmap()}</div></div>
<div class="blk"><div class="card">{moves()}</div>
<div class="take">We can't out-reach PhonePe or out-spend Jar. Our room is depth: committed savers in one segment, and the assisted lane no app plays in.</div></div>
"""

P7 = f"""
<div class="blk"><h2>5 · Offline is a 20% test, not the bet</h2>
<div class="card">{test_arm()}</div></div>
<div class="blk"><div class="card">{offline_cost()}</div>
<div class="take">Offline is Bachatt's empty square. We test it on ~20% of savers and grow it only where it pays for itself, mostly through credit.</div></div>
"""

P8 = f"""
<div class="blk"><h2>6 · The challenger's slide: same map, different ground</h2>
{slide(CHALLENGER, annotate=True, title="Challenger model", sub="Same three columns · online-first, with a ~20% offline test",
        footer="Vision → the daily money partner for cash earners: save, withdraw, borrow, protect; online first, a person where it pays",
        footer2="Power move: committed savers + their savings record → credit quality an app built for sign-ups can't match")}
<div class="chips">
<div class="chip" style="border-color:{GREEN};color:{GREEN}">TABLE STAKES: match Bachatt online in 6–9 months</div>
<div class="chip" style="border-color:{AMBER};color:{AMBER}">OFFLINE TEST: ~20% of savers, grows only if it pays</div>
<div class="chip" style="border-color:{RED};color:{RED}">CONTESTED: wallet, AI, credit, gold loans</div>
<div class="chip" style="border-color:{BLUE};color:{BLUE}">OUR EDGE (to prove): savings record → better credit</div>
</div></div>
<div class="card">{pilot()}</div>
"""

P9 = f"""
<div class="blk"><h2>7 · Rules and decisions</h2>
<div class="card">{rules()}</div></div>
<div class="blk"><h2>Decisions for us</h2>
<div class="chips">
<div class="chip">① Online-first, with a ~20% offline test arm: agreed?</div>
<div class="chip">② Segment: shopkeepers and vendors first? (vendors saved 2.2× drivers, NG-040)</div>
<div class="chip">③ Credit path: DSA → share risk → LSP → NBFC. When, and who leads?</div>
<div class="chip">④ Kill lines for the 5 pilot gates, agreed now</div>
</div></div>
"""

SOURCES = [
    ("BAC-02/04/05, XB-03, XB-10, XL-12", "Bachatt claims: ~3M users, ₹50 crore+ invested, product shelf, loans up to ₹5 lakh via partner NBFCs on behaviour data", "bachatt.app; press release"),
    ("QM-45", "About $16M raised ($4M seed + $12M Series A, Accel)", "Entrackr"),
    ("NG-032, NG-033, NG-034", "Bachatt discloses no retention; SBI ₹250 daily SIP: 35.6% of FY26 starts stopped by year-end; Chhoti SIP ~20k closures vs ~28k additions a month", "Bachatt; SBI MF RHP via Business Standard; SEBI"),
    ("LEV-040, NG-038, JAR-06/07/11, SAV-08", "Jar ~22 saves a month and 1M+ a day → ~7% of registered active (derived); PhonePe merchants ~24% monthly active; Jar 35M registered, profitable, P2P test; PhonePe Daily Savings with Jar from ₹10 a day", "Deccan Chronicle; TechCrunch; Inc42; Medianama; PhonePe DRHP"),
    ("EVD-01, EVD-02, EVD-03", "US credit-builder RCT: no average effect, 39% late; app data predicted credit for no-history borrowers (Mexico); SHG NPA 2.05% vs microfinance 8.72%", "CFPB/RFS; NBER w33208; NABARD"),
    ("NG-042, NG-015, XB-06", "55% of new small-business borrowers new to credit; self-employed unsecured loans peak 10.2% 90+ (NBFC 11.1%); Paytm 7.5 lakh financial-services customers of 1.51 Cr merchants", "TransUnion CIBIL; CRIF; Paytm Q4 FY26"),
    ("NG-041, NG-040, IV-01/03/11/13", "Pigmy agent commission capped at 2.5% of collections (was 3–4%); Kenya: vendors deposited 2.2× drivers; one co-op collector: 200–400 savers, ₹200–500 a day, most 5+ years", "Indian Cooperative; Dupas & Robinson (2013); our interview, 15 Oct 2026"),
    ("REG-036/037, REG-039, REG-041", "ARN ₹40,000; NISM ₹1,500; trail only on regular plans (liquid ≈8 bp); instant redemption ≤ ₹50,000 / 90% a day", "AMFI, NISM, SEBI"),
    ("REG-022/023, REG-066, REG-081", "No loans against gold ETF/MF units or digital gold; MF payments from the investor's own account; BUDS Act", "RBI; SEBI; India Code"),
    ("XB-04, XL-13, XL-09, XL-29", "Debt-fund trail 0.2–0.5%; DSA 1–2.5%; Paisabazaar ≤ 4.6%; personal-loan average ₹58,522", "AMC blogs; GroMo; PB Fintech; CRIF"),
    ("SE-05, XB-07, LEV-061, LEV-026, LEV-030", "Paytm 4.5–5% per loan; LSP with DLG ~11% gross, ~8–9% net; Stashfin NIM 21.3%, credit cost 8–10%, RoMA 1.2%; fintechs buying NBFCs", "Paytm; Moneyview RHP; ICRA; The Painted Stork"),
    ("QM-12, TB-18, LEND-02", "PhonePe 25,657 field staff + 31,000 agents; Groww cost to acquire ₹796 → ₹1,374; Kissht 53.2M registered", "PhonePe DRHP; Entrackr; OnEMI RHP"),
]


def build():
    src = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in SOURCES)
    p10 = (f'<div class="pb"></div><h2>Sources</h2><p class="small">IDs are rows in our research files. Bachatt and Jar figures are company claims. '
           f'"Our estimate", "our read" and "derived" mark items that are not published facts.</p>'
           f'<table><colgroup><col style="width:24%"><col style="width:52%"><col style="width:24%"></colgroup><tr><th>ID</th><th>What</th><th>Source</th></tr>{src}</table>')
    html = (f'<!doctype html><html><head><meta charset="utf-8"><title>Bachatt memo</title><style>{CSS}</style></head>'
            f'<body>{P1}{P2}{P3}{P4}{P5}{P6}{P7}{P8}{P9}{p10}</body></html>')
    out = HERE / "Bachatt_teardown_memo.html"
    out.write_text(html)
    pdf = HERE / "Bachatt_teardown_memo.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf)


if __name__ == "__main__":
    build()

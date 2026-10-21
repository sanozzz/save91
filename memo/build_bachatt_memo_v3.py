"""Co-founder memo v3 to Piyush: pictorial. Built on the operator's Bachatt Model slide (19 Oct 2026).
Operator: "In the memo also define the pdf slide that I have the bachatt model. That slide defines Bachatt now which
makes the entry clear and future contested." Then: "build it more pictorial, less text more diagrams, flowchart etc".
Pages: 1 the slide + thesis flow; 2 entry = ground floor / contested floors + value per user; 3 credit staircase +
offline-unlocks flowchart; 4 challenger slide; 5 rules map + 6-month pilot timeline + decisions; 6 sources.
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
                          ("✗", "Offline acquisition", "wedge"), ("✓", "Low-ticket entry (~₹250)", "stake"),
                          ("✓", "→ Digital loans through DSA", "stake")]),
    "RETENTION": (RET, [("✓", "Financial products (MF, Insta Fund, Gold/Silver)", "stake"),
                        ("✗", "Wallet-like: save in / withdraw out", "contest"),
                        ("✓", "Daily / flexible SIP for irregular incomes", "stake"), ("✓", "No lock-in, instant withdraw", "stake")]),
    "SERVICING": (SER, [("✗", "① AI financial planning", "contest"), ("✓", "② Lean DSA + digital", "stake"),
                        ("✓", "③ Loans on book*", "contest"), ("✗", "④ 3-month EMI + gold loan", "contest")]),
}
CHALLENGER = {
    "ACQUISITION": (ACQ, [("✓", "Debt-fund savings (match)", "stake"), ("✓", "Online + OFFLINE agents", "wedge"),
                          ("✓", "Cash first → UPI", "stake"), ("✓", "Loans: partner → risk-share → own book", "contest")]),
    "RETENTION": (RET, [("✓", "Same fund shelf (no digital gold)", "stake"), ("✓", "Habit from a person + app", "wedge"),
                        ("✓", "Save in / out on fund rails", "contest"), ("✓", "Never hold money", "stake")]),
    "SERVICING": (SER, [("✓", "AI planning through the agent", "contest"), ("✓", "Collections: agent knows borrower", "wedge"),
                        ("✓", "Credit from the savings record", "contest"), ("✓", "Gold loans: doorstep appraisal", "contest")]),
}
TAG = {"stake": ("TABLE STAKES", LGREEN, GREEN), "contest": ("CONTESTED", LRED, RED), "wedge": ("OUR WEDGE", LAMBER, AMBER)}


def slide(data=BACHATT, annotate=False, title="Bachatt Model", sub="Acquisition + Retention + Servicing",
          footer="Vision → go-to financial planning app / wallet (save in, withdraw out, finance purchases)",
          footer2="Power move: own the customer relationship + money flows → EMI on products deepens habit and data"):
    cols = []
    for name, (col, items) in data.items():
        rows = ""
        for mark, txt, kind in items:
            mc = GREEN if mark == "✓" else RED
            tag = ""
            if annotate or kind == "wedge" and not annotate and False:
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
             (560, LAMBER, AMBER, "★", "OUR WEDGE", ["Offline is Bachatt's empty", "square; it unlocks", "the contested ones"])]
    for x, bg, fg, ic, head, sub in nodes:
        s.append(box(x, 10, 250, 120, bg, fg))
        s.append(T(x + 22, 52, ic, 30, 800, fg))
        s.append(T(x + 62, 46, head, 13.5, 800, fg))
        s.append(lines(x + 62, 70, sub, 11, 500, INK, "start", 15))
    s.append(arrow(262, 70, 283, 70, INK))
    s.append(arrow(537, 70, 558, 70, INK))
    return svg(820, 140, "".join(s))


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
            ("Same loan, we collect + share risk", 58522 * 0.0475, "once", AMBER)]
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
             ("Collect + share risk", "4.5–5%", "SE-05", 3), ("LSP with first-loss", "~8–9% net", "LEV-061", 4),
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
    s.append(T(780, 284, "the edge = credit quality + collections", 10.5, 800, NAVY, "end"))
    return svg(820, 292, "".join(s))


def wedge():
    s = [T(0, 16, "HOW OFFLINE UNLOCKS THE CONTESTED SQUARES", 12, 800, NAVY)]
    cx, cy = 410, 175
    s.append(f'<circle cx="{cx}" cy="{cy}" r="72" fill="{LAMBER}" stroke="{AMBER}" stroke-width="3"/>')
    s.append(lines(cx, cy - 12, ["OFFLINE", "AGENT", "(our wedge)"], 13, 800, AMBER, "middle", 17))
    outs = [(110, 70, "Retention", "a person keeps", "the saver saving", "→ wallet habit"),
            (710, 70, "Collections", "the agent knows", "the borrower", "→ loans on book"),
            (110, 285, "Gold loans", "needs physical gold,", "checked at the door", "(REG-022/023)"),
            (710, 285, "AI planning", "lands through", "someone trusted", "→ action, not advice")]
    for x, y, h, a, b, c in outs:
        s.append(box(x - 105, y - 38, 210, 84, "#fff", RED))
        s.append(T(x, y - 14, h, 13, 800, RED, "middle"))
        s.append(lines(x, y + 6, [a, b, c], 10.5, 500, INK, "middle", 13))
        sx = cx + (60 if x > cx else -60)
        sy = cy + (-40 if y < cy else 40)
        ex = x + (-105 if x > cx else 105)
        ey = y + (12 if y < cy else -12)
        s.append(arrow(sx, sy, ex, ey, AMBER, 3))
    s.append(T(410, 360, "Who else wants these: Paytm/PhonePe (wallet, merchants), Jar (daily savings), Snapmint/Bajaj (EMI), Muthoot/Manappuram (gold)", 9.5, 500, MUTED, "middle"))
    return svg(820, 370, "".join(s))


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
    s.append(f'<line x1="40" y1="{y}" x2="780" y2="{y}" stroke="{NAVY}" stroke-width="4"/>')
    ms = [(40, "Month 0", "Launch: 1 city,", "a few agents"), (220, "Month 1–3", "Savers won per", "agent; cost per saver"),
          (420, "Month 3–6", "Still saving at 3 and 6", "months; cash → UPI"), (620, "Month 4–6", "Loan take-up;", "lender terms signed"),
          (780, "Month 6", "GO / STOP", "on agreed lines")]
    for x, h, a, b in ms:
        s.append(f'<circle cx="{x}" cy="{y}" r="12" fill="{NAVY}"/>')
        s.append(T(x, y - 22, h, 11.5, 800, NAVY, "middle"))
        s.append(lines(x, y + 34, [a, b], 10.5, 500, INK, "middle", 13))
    gates = [("Cost per saver kept", "< online's ≈₹500 ÷ 1-in-4"), ("Still saving at 12 months", "clearly above apps' ≈1 in 4"),
             ("Cash → UPI share", "rising every month"), ("Lender terms", "above the 1–3% DSA fee"), ("Gold-loan pilot", "doorstep appraisal works")]
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
<div class="rec"><b>Recommendation:</b> launch only if we lead on <b>offline</b> and <b>credit with collections</b>. Match the ✓ squares fast, and prove the wedge in one city in 6 months.</div>
"""

P2 = f"""
<div class="pb"></div>
<h2>1 · Entry is clear: anyone can build the ground floor</h2>
<div class="card">{building()}</div>
<div class="take">Copying Bachatt's ✓ squares gets us parity at best. The market will be won on the contested floors.</div>
<div class="card">{value()}</div>
<div class="take">Savings trail is under ₹1 a user a year at Bachatt's visible balances (~{inr(PER_USER)} a user). One loan is worth more than years of trail.</div>
"""

P3 = f"""
<div class="pb"></div>
<h2>2 · The money is in credit, and power is in collections</h2>
<div class="card">{staircase()}</div>
<div class="take">A licence alone doesn't make an NBFC profitable: fintech NBFCs keep about 1% after losses. The edge is credit quality, from the savings record plus collections.</div>
<div class="card">{wedge()}</div>
<div class="take">Offline is Bachatt's empty square, and it is the key that unlocks the four contested ones.</div>
"""

P4 = f"""
<div class="pb"></div>
<h2>3 · The challenger's slide: same map, different ground</h2>
{slide(CHALLENGER, annotate=True, title="Challenger model", sub="Same three columns · we compete on the contested squares",
        footer="Vision → the trusted daily money partner for cash earners: save, withdraw, borrow, protect, with a person behind the app",
        footer2="Power move: a person + the savings record + collections → credit quality an app alone can't match")}
<div class="chips">
<div class="chip" style="border-color:{GREEN};color:{GREEN}">TABLE STAKES: match Bachatt in 6–9 months</div>
<div class="chip" style="border-color:{AMBER};color:{AMBER}">OUR WEDGE: offline agents, habit, collections</div>
<div class="chip" style="border-color:{RED};color:{RED}">CONTESTED: wallet, AI, credit, gold loans</div>
<div class="chip">THREAT: Bachatt adds offline with its $16M (QM-45)</div>
</div>
"""

P5 = f"""
<div class="pb"></div>
<h2>4 · Rules, proof, decisions</h2>
<div class="card">{rules()}</div>
<div class="card">{pilot()}</div>
<h2>Decisions for us</h2>
<div class="chips">
<div class="chip">① Fight on the contested squares, with offline as the wedge?</div>
<div class="chip">② First city and segment: e.g. NCR shopkeepers?</div>
<div class="chip">③ Credit path: DSA → risk-share → NBFC. When, and who leads?</div>
<div class="chip">④ Kill lines for the 5 pilot numbers, agreed now</div>
</div>
"""

SOURCES = [
    ("BAC-02/04/05, XB-03, XL-12", "Bachatt claims: ~3M users, ₹50 crore+ invested, product shelf, loans via partner NBFCs", "bachatt.app; press release"),
    ("QM-45", "About $16M raised ($4M seed + $12M Series A, Accel)", "Entrackr"),
    ("REG-036/037, REG-039, REG-041", "ARN ₹40,000; NISM ₹1,500; trail only on regular plans (liquid ≈8 bp); instant redemption ≤ ₹50,000 / 90% a day", "AMFI, NISM, SEBI (research/regulation_rails.csv)"),
    ("REG-022/023", "RBI Gold Lending Directions 2025: no loans against gold ETF/MF units or digital gold", "RBI (research/regulation_rails.csv)"),
    ("REG-066, REG-081", "MF payments from the investor's own account; BUDS Act on unregulated deposits", "SEBI; India Code"),
    ("XB-04, XL-13, XL-09, XL-29", "Debt-fund trail 0.2–0.5%; DSA 1–2.5%; Paisabazaar ≤ 4.6%; personal-loan average ₹58,522", "AMC blogs; GroMo; PB Fintech; CRIF"),
    ("SE-05, XB-07, LEV-061, LEV-026", "Paytm 4.5–5% per loan; LSP with DLG ~11% gross; Stashfin NIM 21.3%, credit cost 8–10%, RoMA 1.2%", "Paytm; Moneyview RHP; ICRA"),
    ("QM-12, TB-18", "PhonePe 25,657 field staff + 31,000 agents; Groww cost to acquire ₹796 → ₹1,374", "PhonePe DRHP; Entrackr"),
]


def build():
    src = "".join(f"<tr><td>{a}</td><td>{b}</td><td>{c}</td></tr>" for a, b, c in SOURCES)
    p6 = (f'<div class="pb"></div><h2>Sources</h2><p class="small">IDs are rows in our research files. Bachatt figures are company claims. '
          f'"Our estimate" and "to verify" mark items that are not sourced facts.</p>'
          f'<table><colgroup><col style="width:24%"><col style="width:52%"><col style="width:24%"></colgroup><tr><th>ID</th><th>What</th><th>Source</th></tr>{src}</table>')
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>Bachatt memo</title><style>{CSS}</style></head><body>{P1}{P2}{P3}{P4}{P5}{p6}</body></html>'
    out = HERE / "Bachatt_teardown_memo.html"
    out.write_text(html)
    pdf = HERE / "Bachatt_teardown_memo.pdf"
    subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf)


if __name__ == "__main__":
    build()

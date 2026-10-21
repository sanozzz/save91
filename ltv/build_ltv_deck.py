"""LTV/CAC deck (operator 21 Oct 2026): "There should have a separate deck for LTV CAC Calculations and explain each assumption
and then use that". Taps: online AND doorstep savers; ~15 pages + an appendix. Every number comes from the same one-saver model
the workbook "SaveMore || LTVCAC" replays cell by cell (model/ltv_book.py): tables/ltv_*.csv and online_loan_funnel.csv.
Design: the v4 deck's pages (seed/build_seed_plan.py CSS). Builds ltv/LTV_CAC_deck.html and .pdf."""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(ROOT / "seed"))
sys.path.insert(0, str(ROOT / "model"))
import build_seed_plan as sp  # noqa: E402
import cohort_engine as ce  # noqa: E402
import ltv_book as lb  # noqa: E402
import online_plan as op  # noqa: E402

TAB = ROOT / "tables"
INK, NAVY, TEAL, AMBER, SLATE, MUTE, LINE, BG, RED = sp.INK, sp.NAVY, sp.TEAL, sp.AMBER, sp.SLATE, sp.MUTE, sp.LINE, sp.BG, sp.RED
NAVY2, NAVY3, NAVY4 = sp.NAVY2, sp.NAVY3, sp.NAVY4
LATE = "#a8553d"
T, R, A, svg = sp.T, sp.R, sp.A, sp.svg
FOOT = "LTV/CAC: what one saver is worth · October 2026 · Confidential"
SHEET_URL = "docs.google.com/spreadsheets/d/1VdZy4vSSaTQmrp--txW31fjN8nHlF2iLQnLsUeAKTP4"

BASE = lb.base_params()
ON, DR, _ = lb.evaluate(BASE, door_cac=False)
P = op.profiles(op.saver_inputs())
X = op.saver_inputs()
REACH = op.LOAN_REACH
CAC, DCAC = op.CAC, lb.DOOR_CAC
OAT = pd.read_csv(TAB / "ltv_one_at_a_time.csv").set_index("key")
MC = pd.read_csv(TAB / "ltv_mc_draws.csv")
DRV = pd.read_csv(TAB / "ltv_drivers.csv").set_index("key")
FUN = pd.read_csv(TAB / "online_loan_funnel.csv").set_index("stage")
def at(**kw):
    """The online saver with some inputs changed, everything else at the plan."""
    pp = dict(BASE)
    pp.update(kw)
    return lb.evaluate(pp, door_cac=False)[0]


def pass_line(k, lo, hi, target=3.0):
    """The value of one input at which online LTV/CAC crosses the target (None if it never does in [lo, hi])."""
    f = lambda v: at(**{k: v})["ltvcac"] - target
    flo = f(lo)
    if flo * f(hi) > 0:
        return None
    for _ in range(40):
        m = (lo + hi) / 2
        lo, hi = (m, hi) if f(m) * flo > 0 else (lo, m)
    return (lo + hi) / 2


AP2 = at(on_apply=0.02)
VAL_SHOW = {"nps_comm": "₹200 once", "recharge_renew": "100%", "bills_renew": "100%", "bills_ticket": "24 bills a year"}
LINES = [("fund", "Fund fees", NAVY), ("pb", "Personal + business loans", NAVY3), ("ol", "Other lenders' loans", NAVY4),
         ("ins", "Insurance", TEAL), ("cards", "Cards", "#7cc4b8"), ("oth", "Other products", "#9fb3c8")]


def page(n, section, kicker, title, body, src=""):
    s = f'<div class="src">{src}</div>' if src else ""
    return f"""<section class="page">
<header class="ph"><span class="brand">{sp.NAME} <em>· working name</em></span><span>{section}</span></header>
<div class="kicker">{kicker}</div><h1>{title}</h1>
<div class="body">{body}</div>{s}
<footer class="pf"><span>{FOOT}</span><span>{n}</span></footer>
</section>"""


def table(head, rows, widths=None, size=12, compact=False, extra=""):
    cg = "".join(f'<col style="width:{w}%">' for w in widths) if widths else ""
    th = "".join(f"<th>{h}</th>" for h in head)
    tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f'<table class="{"at compact" if compact else "at"} {extra}" style="font-size:{size}px"><colgroup>{cg}</colgroup><tr>{th}</tr>{tr}</table>'


def ind(v):
    n = f"{abs(v):.0f}"
    head, tail = n[:-3], n[-3:]
    while len(head) > 2:
        tail = head[-2:] + "," + tail
        head = head[:-2]
    return ("−" if v < 0 else "") + (head + "," + tail if head else tail)


def rs(v):
    return ("−" if v < 0 else "") + f"₹{ind(abs(v))}"


def pct(v, d=0):
    s = f"{v * 100:.{d}f}"
    return (s.rstrip("0").rstrip(".") if d else s) + "%"


def fmt(v, fm):
    if fm in ("pct", "pct2", "pct3"):
        return pct(v, 2 if v < 0.1 else 1) if v else "0%"
    if fm in ("rs", "rs2"):
        return rs(v) if abs(v) >= 10 else f"₹{v:g}"
    return f"{v:g}"


def short_rs(v, fm):
    if fm in ("rs", "rs2") and v >= 1e5:
        return f"₹{v / 1e5:g} lakh"
    if fm in ("rs", "rs2") and v >= 1e4:
        return f"₹{v / 1e3:g}k"
    return fmt(v, fm)


def clip(s, n):
    s = str(s)
    return s if len(s) <= n else s[:s.rfind(" ", 0, n)] + "…"


def x(v):
    return f"{v:.1f}×"


def eff(k):
    r = OAT.loc[k]
    return float(r["on_lo"]), float(r["on_hi"]), int(r["pay_lo"]), int(r["pay_hi"]), float(r["door_lo"]), float(r["door_hi"])


INP = {k: (g, lab, val, unit, mck, src, why, fm) for g, k, lab, val, unit, mck, src, why, fm in lb.inputs_list()}
SHORT_SRC = {   # one line each for the story pages; the full text is on the workbook's Inputs tab and in the appendix
    "cac_on": "Founder's judgement; seed funnel budget ₹600", "cac_door": "Our business-plan model, at scale",
    "r3_on": "SBI MF daily SIP's steady drop (NG-033)", "r12_on": "SBI MF ₹250 daily SIP, extended to 12 months",
    "r3_door": "Agent's existing book ~92% (IV-12)", "r12_door": "Agreed; agent's book ~72% (IV-01, IV-12)",
    "churn_late": "US micro-investing app ~1% (TB-11)", "daily": "A daily-savings app's minimum", "days": "Our judgement (a shop opens ~26 days)",
    "amount_growth": "Our judgement; no data", "withdraw_m": "Our judgement; no data", "rollover": "Product design (an SIP runs on)",
    "eq_share": "Conversation with a daily-savings app", "eq_return": "Our estimate (conservative)", "debt_return": "Liquid funds 5–6% (OWN-02)",
    "eq_trail": "Listed distributor 0.88–0.91% (XO-08)", "debt_trail": "Fund guides 0.2–0.5% (XB-04)",
    "reach_on": "5 sign-ups a saver, half finish KYC", "loan_apply": "Founder's judgement; no observed rate", "mix_pb": "Founder's judgement (XF rows)",
    "mix_gold": "Founder's judgement (XF rows)", "mix_lap": "Founder's judgement (XF rows)", "mix_home": "Founder's judgement (XF rows)",
    "approved_first": "Founders' past data ~25% (XF-24)", "approved_repeat": "Listed lender: 74% of repeat (XL-41)",
    "ticket": "Digital loans ₹19k–70k (XF-11)", "fee": "DSA rate cards 1–2.5% (XF-01)", "tenure": "Research: 12–24 months",
    "topup_share": "Our judgement; lenders top up good payers", "support_cost": "Founder's figure", "tech": "Our judgement",
    "early_takeup_mult": "Founder's judgement", "early_approval_mult": "New vs repeat approval gap (XL-41)",
    "takeup_growth": "Our judgement; no data", "approval_growth": "Our judgement (lenders see repayments)", "year_cap": "Model rule"}
DECK_WORDS = lb.PLAIN   # the same investor wording as the workbook


def deck_words(t):
    return lb.plain(t)


def tidy(t):
    t = deck_words(str(t))
    t = re.sub(r"Rs\.?\s?(?=\d)", "₹", t)
    t = re.sub(r"%(\s*%)+", "%", t).replace("Payout: DSA payout:", "DSA payout:")
    t = re.sub(r"₹(\s*₹)+", "₹", t)
    return re.sub(r"\s*₹\s*$", "", t).strip()


def largest_remainder(vals):
    """Round each value so the rounded parts add up to the rounded total."""
    fl = [int(v) for v in vals]
    need = round(sum(vals)) - sum(fl)
    for i in sorted(range(len(vals)), key=lambda i: vals[i] - fl[i], reverse=True)[:max(need, 0)]:
        fl[i] += 1
    return fl


def cut(t, n):
    """Cut at a clause boundary ('; ') when possible, else at a word."""
    t = str(t)
    if len(t) <= n:
        return t
    parts, out = t.split("; "), ""
    for q in parts:
        if len(out) + len(q) + 2 > n:
            break
        out = f"{out}; {q}" if out else q
    return out if out else clip(t, n)


def inputs_table(keys, size=10.5):
    rows = []
    for k in keys:
        g, lab, val, unit, mck, src, why, fm = INP[k]
        spec = lb.ALLSPEC.get(mck) if mck else None
        rng = f"{short_rs(spec[1], fm)} – {short_rs(spec[3], fm)}" if spec and spec[0] != "fixed" and spec[1] != spec[3] else "fixed"
        rows.append([clip(deck_words(lab), 38), f"<b>{VAL_SHOW.get(k) or short_rs(val, fm)}</b>", rng, SHORT_SRC.get(k) or cut(tidy(lb.clean(lb.neutral(src))), 40)])
    return table(["Assumption", "Value", "Range we test", "Where it comes from"], rows, [37, 9, 15, 39], size, compact=True)


def mini_tornado(items, W=520, title="ONLINE LTV/CAC (5 YEARS) AT EACH END OF THE TESTED RANGE", door=False):
    """items: (label, low LTV, high LTV) on one axis; the line is the plan's value."""
    base = DR["ltvcac"] if door else ON["ltvcac"]
    lo = min(min(a, b) for _l, a, b in items + [("", base, base)])
    hi = max(max(a, b) for _l, a, b in items + [("", base, base)])
    lo, hi = min(lo, base * 0.6), max(hi, base * 1.4)
    x0, x1 = 210, W - 46
    X_ = lambda v: x0 + (x1 - x0) * (v - lo) / (hi - lo)
    s = [T(0, 14, title, 10.5, 700, SLATE, ls=1.0)]
    for i, (lab, a, b) in enumerate(items):
        y = 26 + i * 28
        m_ = re.match(r"^(.*?)(\S+) / (\S+)(.*)$", lab)
        if a > b and m_:                                   # the label's order follows the bar: left value first
            lab = f"{m_.group(1)}{m_.group(3)} / {m_.group(2)}{m_.group(4)}"
        s.append(T(0, y + 15, clip(lab, 36), 11.5, 600))
        l_, r_ = sorted((a, b))
        s.append(R(X_(l_), y + 5, max(X_(r_) - X_(l_), 3), 14, NAVY4, r=4))
        s.append(T(X_(a) + (-6 if a <= b else 6), y + 16, x(a), 11, 700, LATE if a < base else NAVY, "end" if a <= b else "start"))
        s.append(T(X_(b) + (6 if b >= a else -6), y + 16, x(b), 11, 700, NAVY if b > base else LATE, "start" if b >= a else "end"))
    yb = 26 + len(items) * 28
    s.append(f'<line x1="{X_(base)}" y1="24" x2="{X_(base)}" y2="{yb}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    s.append(T(X_(base), yb + 14, f"plan {base:.2f}×", 11, 700, INK, "middle"))
    return svg(W, yb + 20, "".join(s))


def chips(items):
    return '<div class="chips3" style="margin-top:12px">' + "".join(f'<div class="chip"><b>{a}</b>{b}</div>' for a, b in items) + "</div>"


def two(left, right, lw=600):
    return f'<div style="display:flex;gap:30px;align-items:flex-start"><div style="flex:0 0 {lw}px">{left}</div><div style="flex:1">{right}</div></div>'


# ------------------------------------------------------------------------------------------------------------------ pages
MC_ON = MC["on_ltv60"]
MC_P10, MC_P50, MC_P90 = (float(np.percentile(MC_ON, q)) for q in (10, 50, 90))
SH3 = float((MC_ON >= 3).mean())
SH24 = float((MC["on_pay"] <= 24).mean())


def cover():
    c600 = eff("cac")[1]
    tiles = [(x(ON["ltvcac"]), f"one online saver: {rs(CAC)} to win, {rs(ON['ltv'])} back over five years after serving costs; paid back in month {ON['pay']}. At the seed's ₹600: {x(c600)}"),
             (x(DR["ltvcac"]), f"one doorstep saver: {rs(DCAC)} to win all-in, {rs(DR['ltv'])} back; paid back in month {DR['pay']}"),
             (f"{x(MC_P50)} median", f"across 1,000 simulated futures (our own ranges, not observed odds): {SH3:.0%} at 3× or better, 1 in 10 below {x(MC_P10)}"),
             ("6 numbers", "decide it: loan size, how many apply for a loan, the cost to win, the daily amount, the loan payout and how many keep saving. Each is shown with its source, range and effect.")]
    t = "".join(f'<div class="ctile"><div class="cbig" style="font-size:34px">{a}</div><div class="csub">{b}</div></div>' for a, b in tiles)
    return f"""<section class="page cover">
<div class="cleft">
  <div class="cbrand">{sp.NAME}</div><div class="cwork">Working name, to be finalised</div>
  <div class="ctitle" style="font-size:50px">What one saver is worth</div>
  <div class="ctag">LTV/CAC, assumption by assumption: the number, where it comes from, how far it could be wrong, and what that does.</div>
  <div class="cmeta">October 2026 · Confidential</div>
</div>
<div class="cright"><div class="cgrid">{t}</div>
<div class="cnote" style="margin-top:22px">The same model as the business plan, rebuilt in a live workbook cell by cell. The arithmetic is checked to the rupee; the assumptions are ours.
Change one in the workbook and the per-saver answer moves live; the 1,000 futures are rerun on request.</div></div>
</section>"""


def flow_svg():
    W, H = 1152, 284
    s = []
    box = lambda x_, y_, w, h, t1, t2, col: (R(x_, y_, w, h, "#fff", col, 12, 2) + T(x_ + 14, y_ + 26, t1, 14, 700, col) + T(x_ + 14, y_ + 46, t2, 11.5, 500, SLATE))
    s.append(box(0, 110, 200, 70, "A saver won", "₹450 online, ₹404 doorstep", TEAL))
    s.append(box(250, 10, 250, 70, "Keeps saving (or stops)", "80% at month 3, 38% at a year online", NAVY))
    s.append(box(250, 110, 250, 70, "Saves ₹100 a day", "~₹2,000 a month into funds, 80/20", NAVY))
    s.append(box(250, 210, 250, 70, "Comes with 2.5 KYC'd users", "5 sign-ups per saver, half finish KYC", NAVY))
    s.append(box(560, 10, 270, 70, "Products, insurance, cards", "commission on what savers buy", NAVY4))
    s.append(box(560, 110, 270, 70, "Fund balance → our trail", "0.67% a year on the balance", NAVY4))
    s.append(box(560, 210, 270, 70, "35% apply for a loan a year", "30% approved first time, 70% repeat", NAVY4))
    s.append(box(890, 60, 262, 70, "Revenue less serving = LTV", "support ₹5 + tech ₹1 a saver a month", INK))
    s.append(box(890, 170, 262, 70, "LTV ÷ cost to win = LTV/CAC", "pays back when it reaches ₹450", INK))
    for (x1_, y1_, x2_, y2_) in ((200, 145, 250, 45), (200, 145, 250, 145), (200, 145, 250, 245), (500, 45, 560, 45), (500, 145, 560, 145),
                                 (500, 245, 560, 245), (830, 45, 890, 95), (830, 145, 890, 95), (830, 245, 890, 95), (1021, 130, 1021, 170)):
        s.append(A(x1_, y1_, x2_, y2_, MUTE, 1.8))
    return svg(W, H, "".join(s))


def p_how(n):
    body = flow_svg() + chips([
        ("Saver won, not sign-up", "A saver is someone who starts saving. Online, 1 in 5 sign-ups does; the cost to win is everything spent to get one saver."),
        ("Undiscounted, 5 years (8 alongside)", "LTV = what a saver brings in less what it costs to serve them while they save. No discounting: the cumulative rupees."),
        ("The cautious saver", "The answer is for a saver who joins early, before take-up and approvals have grown with the business's track record (they grow to year 5), at the post-seed ₹450 to win. Later savers are worth more.")])
    gl = ('<div style="margin-top:8px;font-size:11px;color:#475569;line-height:1.4"><b style="color:#12355b">Words used here.</b> '
          "<b>KYC'd</b>: finished the identity check. <b>Trail</b>: the yearly share of a fund's fee paid to its distributor. <b>SIP</b>: a regular instalment into a mutual fund. "
          "<b>NBFC</b>: a non-bank lender. <b>DSA</b>: an agent paid by a lender for referred loans. <b>EMI</b>: a loan instalment. <b>LAP</b>: a loan against property. "
          "<b>Doorstep</b>: a field agent signs the saver in person. <b>The seed</b>: the first 18 months. <b>Futures</b>: simulated draws of all inputs together.</div>")
    body += gl
    return page(n, "How we count", "THE DEFINITION", "One saver's value is three streams (the fund, loans, other products) for as long as they keep saving, less serving, against the cost to win them",
                body, "Not in this view: the team, office and brand, the 10% contingency, the two-month wait for fees, tax. The app never holds the money; loans are made by banks and NBFCs.")


def waterfall():
    items = [("Cost to win", -CAC)] + [(lab, ON[k]) for k, lab, _c in LINES] + [("Serving", ON["serve"])]
    W, H, x0, y0, y1 = 590, 320, 6, 50, 246
    lvl, bars = 0.0, []
    for nm, v in items:
        bars.append((nm, lvl, lvl + v))
        lvl += v
    bars.append(("Net, 5 years", 0.0, lvl))
    lo, hi = min(min(a, b) for _n, a, b in bars), max(max(a, b) for _n, a, b in bars)
    Y = lambda v: y1 - (y1 - y0) * (v - lo) / (hi - lo)
    bw, gap = 52, 12
    col = {"Cost to win": TEAL, "Serving": SLATE, "Net, 5 years": NAVY2}
    col.update({lab: c for _k, lab, c in LINES})
    s = [T(0, 14, "ONE ONLINE SAVER WON, FIRST 5 YEARS (₹)", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0}" y1="{Y(0)}" x2="{x0 + len(bars) * (bw + gap)}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>')
    for i, (nm, a, b) in enumerate(bars):
        xx = x0 + i * (bw + gap)
        s.append(R(xx, min(Y(a), Y(b)), bw, max(abs(Y(a) - Y(b)), 2), col[nm], r=4))
        v = b - a
        ty = min(Y(a), Y(b)) - 7 if v >= 0 else max(Y(a), Y(b)) + 16
        s.append(T(xx + bw / 2, ty, (("+" if v >= 0 else "−") + rs(abs(v))) if nm != "Net, 5 years" else rs(v), 12.5, 800 if nm.startswith("Net") else 700, col[nm], "middle"))
        lines_ = []
        for w_ in nm.split(" "):                       # greedy wrap, about 11 characters a line
            if lines_ and len(lines_[-1]) + len(w_) + 1 <= 11:
                lines_[-1] += " " + w_
            else:
                lines_.append(w_)
        for j, ln in enumerate(lines_):
            s.append(T(xx + bw / 2, y1 + 34 + j * 13, ln, 10.5, 700 if nm.startswith("Net") else 600, INK if nm.startswith("Net") else SLATE, "middle"))
        if i < len(bars) - 2:
            s.append(f'<line x1="{xx + bw}" y1="{Y(b)}" x2="{xx + bw + gap}" y2="{Y(b)}" stroke="{MUTE}" stroke-dasharray="3 3"/>')
    return svg(W, H, "".join(s))


def p_answer(n):
    rows = []
    for k, lab, _c in [("cac", "Cost to win", None)] + [(k_, {"pb": "Personal + business", "ol": "Other lenders"}.get(k_, l_), c_) for k_, l_, c_ in LINES] + [("serve", "Serving", None)]:
        if k == "cac":
            rows.append([lab, rs(-CAC), rs(-DCAC), rs(-CAC), rs(-DCAC)])
        else:
            rows.append([lab, rs(ON[k]), rs(DR[k]), rs(ON[k + "96"]), rs(DR[k + "96"])])
    rows.append(["<b>Net</b>", f"<b>{rs(ON['net'])}</b>", f"<b>{rs(DR['net'])}</b>", f"<b>{rs(ON['net96'])}</b>", f"<b>{rs(DR['net96'])}</b>"])
    rows.append(["<b>LTV/CAC</b>", f"<b>{ON['ltvcac']:.2f}×</b>", f"<b>{DR['ltvcac']:.2f}×</b>", f"<b>{ON['ltvcac96']:.2f}×</b>", f"<b>{DR['ltvcac96']:.2f}×</b>"])
    rows.append(["Pays back", f"month {ON['pay']}", f"month {DR['pay']}", "—", "—"])
    tb = table(["₹ per saver won", "Online, 5 years", "Doorstep, 5 years", "Online, 8 years", "Doorstep, 8 years"], rows, [28, 18, 18, 18, 18], 11, compact=True)
    xs = (ON["rev"] - ON["fund"]) / ON["rev"]
    only = eff("on_reach")[0]
    gap = ON["ltv"] - only * CAC
    body = two(waterfall(), tb, 590) + chips([
        ("Loans are the biggest stream", f"{rs(ON['pb'] + ON['ol'])} of {rs(ON['rev'])}: {(ON['pb'] + ON['ol']) / ON['rev']:.0%} of revenue. Fund fees are {ON['fund'] / ON['rev']:.0%}; insurance, cards and other products {(ON['ins'] + ON['cards'] + ON['oth']) / ON['rev']:.0%}."),
        ("Doorstep: more saving, fewer loans", f"More doorstep savers keep saving ({DR['s12']:.0%} vs {ON['s12']:.0%} at a year), so the fund earns {rs(DR['fund'])} vs {rs(ON['fund'])}; but a doorstep saver brings no extra KYC'd users."),
        ("Cross-sell is {:.0%} of revenue".format(xs), f"Everything except the fund trail is earned on what users borrow or buy through us. About {rs(round(gap, -1))} of the {rs(ON['ltv'])} comes from loans to KYC'd sign-ups who never save; with offers to savers only, LTV/CAC is {x(only)}.")])
    return page(n, "The answer", "LTV / CAC", f"An online saver costs {rs(CAC)} and returns {rs(ON['ltv'])} over five years: {ON['ltvcac']:.1f}×, paid back in month {ON['pay']}; "
                f"a doorstep saver {DR['ltvcac']:.1f}×, month {DR['pay']}", body,
                f"{rs(ON['rev'])} revenue − {rs(-ON['serve'])} serving = {rs(ON['ltv'])} returned; less {rs(CAC)} to win = {rs(ON['net'])} net. Live in the workbook, tab LTV-CAC. Rounded; rows may not add exactly.")


def payback_svg():
    W, H, x0, x1, y0, y1 = 560, 300, 58, 548, 40, 250
    con, cdr = ON["_cum"], DR["_cum"]
    lo, hi = min(con.min(), cdr.min(), -CAC), max(con.max(), cdr.max())
    Xm = lambda m: x0 + (x1 - x0) * m / 96
    Y = lambda v: y1 - (y1 - y0) * (v - lo) / (hi - lo)
    s = [T(0, 14, "CUMULATIVE ₹ PER SAVER WON, AFTER THE COST TO WIN", 11.5, 700, SLATE, ls=1.1)]
    s.append(f'<line x1="{x0}" y1="{Y(0)}" x2="{x1}" y2="{Y(0)}" stroke="{INK}" stroke-width="1.2"/>')
    for m in range(0, 97, 12):
        s.append(T(Xm(m), y1 + 18, str(m), 11, 600, MUTE, "middle"))
    s.append(T(x1, y1 + 34, "months after the saver joins", 11, 600, MUTE, "end"))
    for v in (-CAC, 0, 2000, 4000):
        if lo <= v <= hi:
            s.append(T(x0 - 6, Y(v) + 4, ("−" if v < 0 else "") + rs(abs(v)) if v else "0", 10.5, 600, MUTE, "end"))
    s.append(f'<line x1="{Xm(60)}" y1="{y0}" x2="{Xm(60)}" y2="{y1}" stroke="{LINE}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    s.append(T(Xm(60) + 4, y0 + 8, "5 years", 11, 700, MUTE))
    for arr, col, w, dash in ((cdr, AMBER, 2.4, ' stroke-dasharray="6 4"'), (con, NAVY, 3, "")):
        pts = f"{Xm(0):.1f},{Y(-CAC if col == NAVY else -DCAC):.1f} " + " ".join(f"{Xm(m + 1):.1f},{Y(v):.1f}" for m, v in enumerate(arr))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="{w}"{dash}/>')
    s.append(f'<circle cx="{Xm(ON["pay"])}" cy="{Y(0)}" r="5" fill="{NAVY}"/><circle cx="{Xm(DR["pay"])}" cy="{Y(0)}" r="5" fill="{AMBER}"/>')
    s.append(f'<line x1="{x0 + 10}" y1="{y0 + 6}" x2="{x0 + 40}" y2="{y0 + 6}" stroke="{NAVY}" stroke-width="3"/>' + T(x0 + 48, y0 + 10, f"online: pays back in month {ON['pay']}", 12, 700, NAVY))
    s.append(f'<line x1="{x0 + 10}" y1="{y0 + 26}" x2="{x0 + 40}" y2="{y0 + 26}" stroke="{AMBER}" stroke-width="2.4" stroke-dasharray="6 4"/>' + T(x0 + 48, y0 + 30, f"doorstep: month {DR['pay']}", 12, 700, AMBER))
    s.append(T(x1, Y(con[-1]) - 8, rs(con[-1]), 12, 800, NAVY, "end"))
    return svg(W, H, "".join(s))


def stack_svg():
    W, H, x0, x1, y0, y1 = 560, 300, 40, 548, 30, 226
    m = ON["_m"]
    tot = sum(m[k] for k, _l, _c in LINES)
    hi = float(tot.max()) * 1.1
    Xm = lambda i: x0 + (x1 - x0) * i / 95
    Y = lambda v: y1 - (y1 - y0) * v / hi
    s = [T(0, 14, "₹ A MONTH FROM ONE ONLINE SAVER WON, BY STREAM", 11.5, 700, SLATE, ls=1.1)]
    cum = np.zeros(96)
    for k, lab, c in LINES:
        top = cum + m[k]
        pts = " ".join(f"{Xm(i):.1f},{Y(v):.1f}" for i, v in enumerate(top)) + " " + " ".join(f"{Xm(i):.1f},{Y(v):.1f}" for i, v in reversed(list(enumerate(cum))))
        s.append(f'<polygon points="{pts}" fill="{c}" opacity="0.92"/>')
        cum = top
    s.append(f'<line x1="{x0}" y1="{y1}" x2="{x1}" y2="{y1}" stroke="{INK}" stroke-width="1.2"/>')
    for mm in range(0, 97, 12):
        s.append(T(Xm(max(mm - 1, 0)), y1 + 18, str(mm), 11, 600, MUTE, "middle"))
    for v in (0, 20, 40):
        if v <= hi:
            s.append(T(x0 - 6, Y(v) + 4, f"₹{v}", 10.5, 600, MUTE, "end"))
    for j, (k, lab, c) in enumerate(LINES):
        lx, ly = x0 + (j % 3) * 180, y1 + 40 + (j // 3) * 18
        s.append(R(lx, ly - 10, 11, 11, c, r=2) + T(lx + 17, ly, lab, 11, 600))
    return svg(W, H, "".join(s))


def p_payback(n):
    m = ON["_m"]
    peak = int(np.argmax(sum(m[k] for k, _l, _c in LINES))) + 1
    body = two(payback_svg(), stack_svg(), 560) + chips([
        ("Why month 19", f"Loans start in month 1 for every KYC'd user, at half the full take-up and 60% of the approvals for six months; a first loan pays {pct(X['fee'])} of ₹1 lakh. The fund trail builds slowly with the balance."),
        (f"A jump in month {peak}", "The first six months run at half the take-up and 60% of the approvals; from month 7 every user applies at the full rate, so first loans peak, then thin as users borrow once and savers stop."),
        ("Then a long tail", f"After year 1, 1.5% of savers stop each month; the fund balance, repeat borrowing and loan offers to KYC'd users who never saved keep paying: {rs(ON['ltv96'] - ON['ltv'])} more in years 6–8.")])
    return page(n, "The answer", "WHEN IT PAYS BACK", f"The online saver earns back the {rs(CAC)} in month {ON['pay']}; the doorstep saver in month {DR['pay']}; by year 8 each has returned about six and a half times its cost",
                body, "Left: cumulative revenue less serving, minus the cost to win (Saver tab, the last column of each saver). Right: the online saver's monthly revenue lines, stacked.")


# ---------- assumption pages
def p_cac(n):
    lo, hi, plo, phi, _dl, _dh = eff("cac")
    funnel = svg(560, 196, "".join([
        T(0, 14, "THE SEED'S BUDGETED FUNNEL: WHAT A SAVER WON COSTS (₹)", 11.5, 700, SLATE, ls=1.1),
        R(0, 34, 250, 54, BG, LINE, 10, 1), T(14, 58, "5 sign-ups × ₹100", 14, 700, NAVY), T(14, 78, "a sign-up, paid acquisition", 11.5, 500, SLATE),
        T(276, 66, "₹500", 18, 800, NAVY),
        R(0, 100, 250, 54, BG, LINE, 10, 1), T(14, 124, "2.5 KYCs × ₹40", 14, 700, NAVY), T(14, 144, "half the sign-ups finish KYC", 11.5, 500, SLATE),
        T(276, 132, "₹100", 18, 800, NAVY),
        f'<line x1="270" y1="166" x2="380" y2="166" stroke="{INK}" stroke-width="1.5"/>',
        T(276, 188, "₹600 in the seed", 18, 800, TEAL), T(400, 66, "1 in 5 sign-ups", 12, 700, SLATE), T(400, 82, "starts saving", 12, 700, SLATE),
        T(400, 118, "₹450 after the seed needs", 12, 700, NAVY), T(400, 134, "₹70 a sign-up, or", 12, 600, SLATE), T(400, 150, "1 in 3.75 saving", 12, 600, SLATE)]))
    left = funnel + inputs_table(["cac_on", "cac_door"])
    right = mini_tornado([("Cost to win ₹300 / ₹600", lo, hi)], 520, "ONLINE LTV/CAC AT ₹300 AND ₹600 TO WIN") + \
        f'<div style="font-size:13px;line-height:1.45;margin-top:10px">Paid back in month <b>{plo}</b> at ₹300 and month <b>{phi}</b> at ₹600 (plan: month {ON["pay"]}).<br>' \
        f'The doorstep cost is worked out, not assumed: agents\' pay, kit, leads, offices and churn divided by the savers they sign, {rs(DCAC)} a saver at scale.</div>'
    body = two(left, right, 600) + chips([
        ("₹450 after the seed", "₹600 is the seed funnel's budget (₹100 a sign-up, 1 in 5 saving), not yet a measurement. ₹450 is the founder's judgement for after the seed, once the brand is known and referrals start."),
        ("₹300 is not our number", "A competitor quoted about ₹300 per 'customer', without saying whether a customer is a sign-up or a saver. We use it only as the good end."),
        ("The seed will measure it", "Cost per sign-up, share finishing KYC and share starting to save are the first three numbers we plan to report from the seed, every month.")])
    return page(n, "Assumption 1", "COST TO WIN A SAVER", f"We assume ₹450 to win an online saver after the seed (the seed is budgeted at ₹600); at ₹300 LTV/CAC is {x(lo)}, at ₹600 {x(hi)}",
                body, "All-in: marketing, onboarding and KYC per saver won. Doorstep, at scale: agent salary, statutory costs, incentive and cash cover ₹26,000 a month; kit ₹12,000; 30% of agents leave a year.")


def retention_svg():
    W, H, x0, x1, y0, y1 = 600, 330, 44, 588, 30, 236
    son, sdr = ON["_s"], DR["_s"]
    Xm = lambda m: x0 + (x1 - x0) * m / 60
    Y = lambda v: y1 - (y1 - y0) * v
    s = [T(0, 14, "SHARE OF SAVERS WON STILL SAVING, MONTHS 0–60", 11.5, 700, SLATE, ls=1.1)]
    for v in (0, 0.25, 0.5, 0.75, 1.0):
        s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{LINE}"/>' + T(x0 - 6, Y(v) + 4, pct(v), 10.5, 600, MUTE, "end"))
    for m in (0, 3, 12, 24, 36, 48, 60):
        s.append(T(Xm(m), y1 + 16, str(m), 11, 600, MUTE, "middle"))
    for arr, col, dash in ((sdr, AMBER, ' stroke-dasharray="6 4"'), (son, NAVY, "")):
        pts = " ".join(f"{Xm(m):.1f},{Y(v):.1f}" for m, v in enumerate(arr[:61]))
        s.append(f'<polyline points="{pts}" fill="none" stroke="{col}" stroke-width="3"{dash}/>')
    marks = [(6, 0.64, "SBI daily SIP: ~64% at ~6 months", NAVY4), (12, 0.24, "savings apps: 24% at a year", LATE), (12, 0.72, "an agent's existing book: ~72%", AMBER)]
    for j, (m, v, lab, c) in enumerate(marks):      # points on the chart, words in the legend below it
        s.append(f'<circle cx="{Xm(m)}" cy="{Y(v)}" r="5" fill="#fff" stroke="{c}" stroke-width="2.5"/>')
        lx, ly = 0, 282 + j * 18
        s.append(f'<circle cx="{lx + 6}" cy="{ly - 4}" r="5" fill="#fff" stroke="{c}" stroke-width="2.5"/>' + T(lx + 16, ly, lab, 11, 700, c))
    s.append(f'<line x1="310" y1="278" x2="336" y2="278" stroke="{NAVY}" stroke-width="3"/>' + T(342, 282, f"online, our plan: {pct(son[60])} at month 60", 11, 700, NAVY))
    s.append(f'<line x1="310" y1="296" x2="336" y2="296" stroke="{AMBER}" stroke-width="3" stroke-dasharray="6 4"/>' + T(342, 300, f"doorstep, our plan: {pct(sdr[60])} at month 60", 11, 700, AMBER))
    return svg(W, H, "".join(s))


def p_retention(n):
    a = eff("on_r12")
    c = eff("churn_late")
    d = eff("r12")
    right = retention_svg()
    left = inputs_table(["r3_on", "r12_on", "r3_door", "r12_door", "churn_late"]) + \
        mini_tornado([("Online: at a year 24% / 45%", a[0], a[1]), ("Stop a month after 12: 1% / 3%", c[0], c[1])], 520, "ONLINE LTV/CAC AT EACH END") + \
        f'<div style="font-size:12.5px;margin-top:4px">Doorstep at 25% / 72% still saving at a year: <b>{x(d[4])}</b> / <b>{x(d[5])}</b> (plan {x(DR["ltvcac"])}).</div>'
    body = two(left, right, 540) + chips([
        ("38% is an extrapolation", "SBI MF's ₹250 daily SIP lost 36% of a year's sign-ups within that year, at an average age of about six months; we extend the same monthly drop to month 12. Nobody has observed our product yet."),
        ("Why the doorstep keeps more", "An agent visits every few days; an existing agent's book keeps about 72% a year. We plan 55% for new doorstep savers, between an app and an existing book."),
        ("After a year, few leave", "Savers who last a year rarely stop: a US micro-investing app loses about 1% a month after month 12; an agent's book about 2.7%. We plan 1.5%.")])
    return page(n, "Assumption 2", "WHO KEEPS SAVING", f"We assume 38 in 100 online savers are still saving after a year (doorstep 55); at 24 LTV/CAC falls to {x(a[0])}, at 45 it rises to {x(a[1])}",
                body, "Monthly drop-off: steady within months 1–3 and within months 4–12 (so 80% at month 3 and 38% at month 12 online), then 1.5% a month for both.")


def balance_svg():
    W, H, x0, x1, y0, y1 = 560, 260, 60, 548, 30, 220
    bal_on = P["balance"][0]
    bal_dr = op.profiles(op.saver_inputs(doorstep=True))["balance"][0]
    hi = max(bal_on.max(), bal_dr.max()) * 1.1
    Xm = lambda m: x0 + (x1 - x0) * m / 96
    Y = lambda v: y1 - (y1 - y0) * v / hi
    s = [T(0, 14, "FUND BALANCE PER SAVER WON (₹, AVERAGE IN THE MONTH)", 11.5, 700, SLATE, ls=1.1)]
    for v in (0, 20000, 40000, 60000):
        if v <= hi:
            s.append(f'<line x1="{x0}" y1="{Y(v)}" x2="{x1}" y2="{Y(v)}" stroke="{LINE}"/>' + T(x0 - 6, Y(v) + 4, rs(v), 10.5, 600, MUTE, "end"))
    for m in range(0, 97, 12):
        s.append(T(Xm(m), y1 + 16, str(m), 11, 600, MUTE, "middle"))
    for arr, col, dash in ((bal_dr, AMBER, ' stroke-dasharray="6 4"'), (bal_on, NAVY, "")):
        s.append(f'<polyline points="{" ".join(f"{Xm(m + 1):.1f},{Y(v):.1f}" for m, v in enumerate(arr))}" fill="none" stroke="{col}" stroke-width="3"{dash}/>')
    s.append(f'<line x1="{x0 + 220}" y1="{y1 - 36}" x2="{x0 + 250}" y2="{y1 - 36}" stroke="{NAVY}" stroke-width="3"/>' + T(x0 + 258, y1 - 32, f"online: {rs(bal_on[-1])} at month 96", 11.5, 700, NAVY))
    s.append(f'<line x1="{x0 + 220}" y1="{y1 - 16}" x2="{x0 + 250}" y2="{y1 - 16}" stroke="{AMBER}" stroke-width="2.4" stroke-dasharray="6 4"/>' + T(x0 + 258, y1 - 12, f"doorstep: {rs(bal_dr[-1])}", 11.5, 700, AMBER))
    return svg(W, H, "".join(s))


def p_saving(n):
    d, dy, w, g = eff("on_daily"), eff("days"), eff("withdraw_m"), eff("amount_growth")
    left = inputs_table(["daily", "days", "amount_growth", "withdraw_m", "rollover"]) + \
        mini_tornado([("Daily amount ₹50 / ₹300", d[0], d[1]), ("Saving days 16 / 24", dy[0], dy[1]), ("Withdraw a month 0% / 3%", w[0], w[1]),
                      ("Step-up a year 0% / 10%", g[0], g[1])], 520, "ONLINE LTV/CAC AT EACH END")
    body = two(left, balance_svg(), 540) + chips([
        ("₹100 a day: a typical starting amount", "A leading daily-savings app's stated minimum is ₹100; daily SIPs start at ₹50; that app's own film shows ₹300. We test ₹50 to ₹300. On about 20 saving days, ₹100 is ₹2,000 a month."),
        (f"{rs(ON['dep'])} saved in five years", f"per online saver won (counting those who stop). The balance earns our trail, so the daily amount moves LTV through the fund fees: {x(d[0])} at ₹50, {x(d[1])} at ₹300."),
        ("Money stays in", "An SIP keeps running, so nothing is paid out at the year end; 1% of the balance is withdrawn each month for emergencies, and a saver who stops takes the balance.")])
    return page(n, "Assumption 3", "HOW MUCH THEY SAVE", f"We assume ₹100 a day on about 20 days a month; at ₹50 LTV/CAC is {x(d[0])}, at ₹300 it is {x(d[1])}", body,
                "Deposits step up 5% each year saved. Balance = last month's balance less withdrawals, plus this month's deposits, plus the fund's return on both.")


def p_fund(n):
    et, es, er, dt = eff("sip_comm"), eff("eq_share"), eff("eq_return"), eff("trail")
    left = inputs_table(["eq_share", "eq_return", "debt_return", "eq_trail", "debt_trail"])
    tor = mini_tornado([("Equity trail 0.5% / 0.9%", et[0], et[1]), ("Equity share 50% / 90%", es[0], es[1]), ("Equity return 6% / 12%", er[0], er[1]),
                        ("Debt trail 0.2% / 0.5%", dt[0], dt[1])], 500, "ONLINE LTV/CAC AT EACH END")
    trail = 0.8 * op.EQ_TRAIL + 0.2 * op.DEBT_TRAIL
    calc = svg(500, 196, "".join([
        T(0, 14, "HOW THE FUND PAYS US", 11.5, 700, SLATE, ls=1.1),
        R(0, 34, 500, 60, BG, LINE, 10, 1), T(16, 60, f"80% equity × {pct(op.EQ_TRAIL, 2)} + 20% debt × {pct(op.DEBT_TRAIL, 2)}", 14, 700, NAVY),
        T(16, 80, "trail commission, paid by the fund house on the balance", 11.5, 500, SLATE),
        T(16, 124, f"= {pct(trail, 2)} a year of the balance", 18, 800, NAVY),
        T(16, 152, f"{rs(ON['fund'])} over 5 years per online saver won", 15, 700, TEAL),
        T(16, 176, f"{rs(DR['fund'])} per doorstep saver (more keep saving)", 13, 600, AMBER)]))
    body = two(left + tor, calc, 600) + chips([
        ("Our own distributor licence (to be registered)", "The one stream we plan to earn on our own registration, paid while the money stays invested, even after a saver stops adding."),
        ("Equity trail ~0.75%", "A listed distributor earns ~0.9% of assets, gross; we use 0.75%. Apps selling direct plans earn nothing."),
        ("Returns matter little", "The fund's return only grows the balance the trail is paid on: 6% or 12% a year moves LTV/CAC by less than 0.1×.")])
    return page(n, "Assumption 4", "THE FUND TRAIL", f"80% equity and 20% debt funds pay us {pct(trail, 2)} a year of the balance: {rs(ON['fund'])} from an online saver over five years, {ON['fund'] / ON['rev']:.0%} of revenue",
                body, "Equity SIP trail 0.5–0.9% (a listed distributor's 0.88–0.91%); debt fund 0.2–0.5% (fund and adviser guides). Debt-only savers would earn the lower trail.")


def funnel_svg():
    rows = [("Sign-ups", FUN.loc["sign-ups", "per 100 savers won"]), ("KYC'd users who see loan offers", FUN.loc["KYC'd users who see loan offers", "per 100 savers won"]),
            ("Still reachable at month 12 (as savers stay)", FUN.loc["still reachable at month 12", "per 100 savers won"]),
            ("Personal + business applications, 5 years", FUN.loc["personal + business loan applications, 5 years", "per 100 savers won"]),
            ("Loans made (first + repeat), 5 years", FUN.loc["personal + business loans (first + repeat), 5 years", "per 100 savers won"])]
    W, x0 = 600, 280
    mx = max(v for _l, v in rows)
    s = [T(0, 14, "PER 100 ONLINE SAVERS WON", 11.5, 700, SLATE, ls=1.1)]
    for i, (lab, v) in enumerate(rows):
        y = 24 + i * 32
        s.append(T(0, y + 17, lab, 12, 600))
        s.append(R(x0, y + 4, (W - x0 - 60) * v / mx, 20, [TEAL, NAVY, NAVY3, NAVY4, NAVY2][i], r=5))
        s.append(T(x0 + (W - x0 - 60) * v / mx + 8, y + 19, f"{v:,.0f}", 12.5, 700))
    return svg(W, 24 + len(rows) * 32, "".join(s))


def p_loans_reach(n):
    rch, ap = eff("on_reach"), eff("on_apply")
    left = funnel_svg() + inputs_table(["reach_on", "loan_apply", "mix_pb", "mix_gold", "mix_lap", "mix_home"])
    right = mini_tornado([("Users reached: savers only / 2.5", rch[0], rch[1]), ("Apply a year: 10% / 50%", ap[0], ap[1])], 520, "ONLINE LTV/CAC AT EACH END") + \
        f'<div style="font-size:13px;line-height:1.45;margin-top:8px">Paid back in month <b>{rch[2]}</b> if offers go to savers only, month <b>{ap[2]}</b> if only 10% apply, '\
        f'month <b>{ap[3]}</b> if half do (plan: month {ON["pay"]}).<br>The apply rate is the plan\'s most fragile number: across the 1,000 futures it moves LTV/CAC more than any other input '\
        f'(rank correlation {DRV.loc["on_apply", "rank corr online LTV/CAC"]:.2f}). The nearest observed rate is 1–2% a year, among merchants on a payments app; at 2%, LTV/CAC would be <b>{x(AP2["ltvcac"])}</b>, '\
        f'paid back in month <b>{AP2["pay"]}</b>.<br>Rules on digital lending and on referral payouts could also change what lenders pay.</div>'
    body = two(left, right, 600) + chips([
        ("Anyone KYC'd, from day 1", "Every sign-up who finishes KYC sees loan offers, saver or not: 2.5 per saver won. One who never saves stays reachable as long as savers do."),
        ("35% apply a year", "The founders' judgement for a credit-hungry segment; about half of fintech borrowers take a new loan within six months. Payments-app merchants: 1–2% a year."),
        ("Split by loan type", "70% personal or business, 15% gold, 3% against property, 2% home; the 10% against the saver's own savings is not counted.")])
    return page(n, "Assumption 5", "LOANS: WHO SEES THE OFFERS, WHO APPLIES", f"We assume loan offers reach 2.5 KYC'd users per online saver and 35% apply a year; offers to savers only give {x(rch[0])}, "
                f"10% applying gives {x(ap[0])}", body, "Doorstep savers: 1 user reached per saver won. Applications use the same monthly chance for every reachable user while they remain.")


def p_loans_pb(n):
    t, f_, a1, a2, tb, tg, ts = (eff(k) for k in ("on_ticket", "on_fee", "on_approved", "approved_repeat", "taken_back", "ticket_growth", "topup_share"))
    first = float(P["loans_first"][0][:60].sum() * REACH * 100)
    rep = float(P["loans_repeat"][0][:60].sum() * REACH * 100)
    top = float(P["topups"][0][:60].sum() * REACH * 100)
    lent = float(P["money_lent"][0][:60].sum() * REACH)
    n1, n2, n3 = largest_remainder([first, rep, top])
    calc = svg(560, 150, "".join([
        T(0, 14, "PER 100 ONLINE SAVERS WON, FIRST 5 YEARS", 11.5, 700, SLATE, ls=1.1),
        T(0, 40, f"{n1} first loans", 15, 700, NAVY), T(170, 40, f"+ {n2} repeat loans", 15, 700, NAVY3), T(355, 40, f"+ {n3} top-up{'s' if n3 != 1 else ''} = {n1 + n2 + n3}", 15, 700, NAVY4),
        T(0, 68, f"about ₹{lent * 100 / 1e5:.0f} lakh lent by banks and NBFCs", 13.5, 700, INK),
        T(0, 92, f"× {pct(X['fee'])} payout rising to {pct(X['fee'] * 1.5)} by month 60, less {pct(X['taken_back'], 1)} of payouts taken back", 12.5, 600, SLATE),
        T(0, 122, f"= {rs(ON['pb'])} per saver won", 19, 800, NAVY), T(250, 122, f"{ON['pb'] / ON['rev']:.0%} of 5-year revenue", 13, 600, SLATE)]))
    left = calc + inputs_table(["approved_first", "approved_repeat", "ticket", "fee", "tenure", "topup_share"])
    right = mini_tornado([("Loan size ₹50k / ₹2 lakh", t[0], t[1]), ("Payout 1% / 3%", f_[0], f_[1]), ("First approval 20% / 45%", a1[0], a1[1]),
                          ("Repeat approval 50% / 85%", a2[0], a2[1]), ("Top-ups a year 5% / 30%", ts[0], ts[1]), ("Next loan bigger 0% / 20%", tg[0], tg[1]),
                          ("Taken back 0% / 5%", tb[0], tb[1])], 520, "ONLINE LTV/CAC AT EACH END")
    body = two(left, right, 600) + chips([
        ("30% first, 70% repeat", "A digital lender approves 11% of new and 74% of repeat applicants; the founders' past lending about 25%. Our 30% sits above both; it rises 10% a year (cap 80%)."),
        ("₹1 lakh, blended", f"Digital personal loans average ₹19,000–70,000; merchant loans ₹50,000–5 lakh (one app's average ₹2 lakh). ₹1 lakh sits above the personal-loan average: at ₹50,000 LTV/CAC is {x(t[0])}."),
        ("A DSA's payout", "Platforms pay DSAs 1–2.5% of a personal loan, up to 3%; we start at 2%, rising to 3% by year 5. Paid by the lender, who takes back 2.5% of payouts (loans cancelled or repaid early).")])
    return page(n, "Assumption 6", "PERSONAL AND BUSINESS LOANS", f"Personal and business loans bring {rs(ON['pb'])} per online saver: {n1 + n2 + n3} loans per 100 savers won over five years, "
                f"at a 2% payout on ₹1 lakh", body, "Tenure 18 months; a borrower can borrow again once repaid; top-ups after 12 EMIs paid. We earn a referral payout only: the lender carries the credit risk.")


def p_loans_other(n):
    rows = []
    names = {"Gold": "loan_gold", "Loan against property": "loan_lap", "Home": "loan_home", "Consumer durable": "loan_cd", "Two-wheeler / e-rickshaw": "loan_vehicle"}
    for nm, q in names.items():
        r = FUN.loc[f"type: {nm}"]
        tk = X[f"{q}_takeup"]
        appr = f"{pct(X[f'{q}_approval'])} approved" if q in ("loan_lap", "loan_home") else "lender's call"
        rows.append([nm, pct(tk, 2), appr, rs(r["average loan Rs"]), pct(r["payout at the start"], 1), f"{r['per 100 savers won']:.1f}", f"<b>{rs(r['our fees Rs per saver won'])}</b>"])
    rows.append(["<b>All other lenders' loans</b>", "", "", "", "", "", f"<b>{rs(ON['ol'])}</b>"])
    tb = table(["Loan", "Apply a year", "Approval", "Loan size", "Our fee", "Loans per 100 savers, 5 y", "₹ per saver won, 5 y"], rows, [20, 12, 14, 13, 10, 15, 16], 11.5, compact=True)
    cd, vt = eff("loan_cd_takeup"), eff("loan_vehicle_ticket")
    lap, hom = eff("loan_lap_approval"), eff("loan_home_approval")
    right = mini_tornado([("Vehicle loan size ₹80k / ₹6 lakh", vt[0], vt[1]), ("Durables take-up 0.5% / 5%", cd[0], cd[1]), ("Property approval 30% / 60%", lap[0], lap[1]),
                          ("Home approval 30% / 60%", hom[0], hom[1])], 1100, "ONLINE LTV/CAC AT EACH END")
    body = tb + '<div style="height:10px"></div>' + right + chips([
        ("Gold: the most common", "Gold loans average ₹1.96 lakh across India; we plan ₹1 lakh for this segment at a 0.5% payout (DSA rates 0.25–1.5%)."),
        ("Property and home: rare but large", "Micro-LAP averages ₹3.9 lakh, affordable housing ₹6–8 lakh; DSA payouts 0.5–1.5% and 0.25–0.75%. Secured, so approval is higher: 45%."),
        ("Durables and vehicles: small", "We have no outside data on take-up or payout for these two; both are our assumptions and together worth about ₹64 a saver.")])
    return page(n, "Assumption 7", "OTHER LENDERS' LOANS", f"Gold, property, home, durable and vehicle loans from other lenders add {rs(ON['ol'])} per online saver; gold loans are a third of it", body,
                "Apply a year for gold, property and home = 35% × that type's share of applications (our assumption). Each type: a monthly chance among users who have not yet bought one; "
                "one referral fee, on disbursal; every KYC'd user reached. Rounded; rows may not add exactly.")


PRODUCTS_SHOW = ["hlth_small", "hlth_family", "life_term", "accident", "two_wheeler", "device", "shop", "choti", "nps", "gold", "fd", "recharge", "bills"]


def p_products(n):
    rows = []
    for q in PRODUCTS_SHOW:
        d = dict((par, X.get(f"{q}_{par}")) for par in ("takeup", "ticket", "comm", "renew"))
        money = float(P[f"rev_xs_{q}"][0][:60].sum())
        kind = lb.PRODUCT_LABEL[q]
        comm = f"₹{d['comm']:g} a bill" if q == "bills" else ("₹200 once" if q == "nps" else ("₹500 at month 24" if q == "choti" else pct(d["comm"], 2)))
        ticket = {"recharge": "₹2,600 a year", "bills": "24 bills a year", "gold": "₹300 a month", "choti": "—", "nps": "—"}.get(q, rs(d["ticket"]))
        rows.append([kind, pct(d["takeup"], 1), ticket, comm, pct(d["renew"]) if d["renew"] is not None else "once", rs(money)])
    rows.append(["Cards (once per saver)", pct(X["card_share"]), "—", f"₹{X['card_fee']:,.0f} a card", "once", rs(ON["cards"])])
    rows.append(["<b>All of these</b>", "", "", "", "", f"<b>{rs(ON['ins'] + ON['cards'] + ON['oth'])}</b>"])
    tb = table(["Product", "Take-up a year", "Ticket", "Our commission", "Renews", "₹ per saver won, 5 y"], rows, [34, 12, 14, 16, 10, 14], 10.5, compact=True)
    ins = eff("ins_partner_share")
    hf = eff("hlth_family_takeup")
    body = tb + chips([
        (f"Small on purpose: {(ON['ins'] + ON['cards'] + ON['oth']) / ON['rev']:.0%} of revenue", "Insurance, cards and everyday products are where we expect to earn on top; we count them cautiously and the plan does not depend on them."),
        ("Insurance through a partner (to be signed)", f"We plan to sell under a broker partner's licence; the partner would keep a quarter, so we would get {pct(X['ins_partner_share'])} of commissions, capped by the regulator's draft (15% first year, 5% on renewals)."),
        ("Widest ranges, smallest effect", f"Every one of these products moves LTV/CAC by 0.2× or less across its whole range (family health cover is the largest: {x(hf[0])} to {x(hf[1])}).")])
    return page(n, "Assumption 8", "INSURANCE, CARDS AND OTHER PRODUCTS", f"Insurance, cards and everyday products add {rs(ON['ins'] + ON['cards'] + ON['oth'])} per online saver over five years; "
                "no single one moves LTV/CAC by more than 0.2×", body,
                "Take-up: share of savers still saving who do not yet hold it, a year. Policies renew each year at the rate shown; habits (gold, recharge, bills) keep running. Money counted while the saver keeps saving. Rounded; rows may not add exactly.")


def p_serve(n):
    sc, tg, ag, et, ea = (eff(k) for k in ("support_cost", "takeup_growth", "approval_growth", "early_takeup_mult", "early_approval_mult"))
    left = inputs_table(["support_cost", "tech", "early_takeup_mult", "early_approval_mult", "takeup_growth", "approval_growth", "year_cap"])
    right = mini_tornado([("Support ₹0 / ₹15 a month", sc[0], sc[1]), ("Take-up growth 0% / 15%", tg[0], tg[1]), ("Approval growth 0% / 20%", ag[0], ag[1]),
                          ("First 6 months' take-up 25% / 75%", et[0], et[1]), ("First 6 months' approval 40% / 80%", ea[0], ea[1])], 520, "ONLINE LTV/CAC AT EACH END")
    body = two(left, right, 600) + chips([
        (f"Serving {rs(-ON['serve'])} over 5 years", "₹5 a month for support, the app, bank charges and supervision, plus ₹1 of tech, for each saver still saving. Sign-ups who never save cost nothing to serve here (an assumption); "
                                                     "compliance and lender integration are company costs, outside this view."),
        ("Slow first months", "A saver of a few weeks is not ready to buy: in months 1–6 every product's take-up is half the full rate and lenders approve 60% as many, because the saving record is thin."),
        ("History helps, but only to year 5", "Each year the business runs, take-up rises 5% and approvals 10% (lenders see repayments); both stop rising after year 5. A saver who joins later starts higher.")])
    return page(n, "Assumption 9", "COST TO SERVE, AND THE FIRST MONTHS", f"Serving costs ₹6 a month per saver still saving (a total of ₹16 gives {x(sc[1])}); the slow first months and a growing track record move LTV/CAC by under 1×",
                body, "Caps: no take-up above 2× the agreed rate, no first-loan approval above 80%.")


SHORT = {"on_ticket": "Personal + business loan size", "on_apply": "Users who apply for a loan a year", "cac": "Cost to win a saver (after the seed)",
         "on_daily": "Daily amount", "on_fee": "Our payout on personal + business loans", "on_r12": "Online: still saving at a year",
         "on_reach": "KYC'd users who see loan offers, per saver", "churn_late": "Share who stop each month after month 12",
         "on_approved": "First loan applications approved", "takeup_growth": "Take-up rises each business year"}


def tornado_svg(k=10):
    d = OAT.head(k).reset_index()
    W, x0 = 1152, 470
    lo = min(d["on_lo"].min(), d["on_hi"].min(), ON["ltvcac"]) * 0.9
    hi = max(d["on_lo"].max(), d["on_hi"].max(), ON["ltvcac"]) * 1.05
    X_ = lambda v: x0 + (W - x0 - 60) * (v - lo) / (hi - lo)
    s = [T(0, 14, "ONLINE LTV/CAC (5 YEARS) WITH EACH INPUT AT THE LOW AND HIGH END OF ITS RANGE, EVERYTHING ELSE AT THE PLAN", 11.5, 700, SLATE, ls=1.1)]
    for i, r in d.iterrows():
        y = 28 + i * 28
        lab = SHORT.get(r["key"], lb.label_of(r["key"]))
        g, *_rest = INP.get({"on_daily": "daily", "on_r12": "r12_on", "cac": "cac_on", "on_apply": "loan_apply", "on_ticket": "ticket", "on_approved": "approved_first",
                             "on_fee": "fee", "on_reach": "reach_on", "eq_share": "eq_share", "sip_comm": "eq_trail"}.get(r["key"], r["key"]), ("",))
        rng_ = f"{fmt(r['low'], 'pct' if r['low'] < 1 and r['high'] <= 1 else 'rs')} – {fmt(r['high'], 'pct' if r['low'] < 1 and r['high'] <= 1 else 'rs')}"
        if r["key"] == "on_reach":
            rng_ = "1 – 2.5 users"
        if r["key"] == "days":
            rng_ = "16 – 24 days"
        if float(r["on_lo"]) > float(r["on_hi"]):                     # read in the bar's order, left to right
            rng_ = " – ".join(reversed(rng_.replace(" users", "").replace(" days", "").split(" – "))) + (" users" if "users" in rng_ else "")
        s.append(T(0, y + 17, clip(lab, 52), 12.5, 600) + T(x0 - 14, y + 17, rng_, 11.5, 600, SLATE, "end"))
        a, b = float(r["on_lo"]), float(r["on_hi"])
        l_, r_ = sorted((a, b))
        s.append(R(X_(l_), y + 5, max(X_(r_) - X_(l_), 3), 18, NAVY4, r=4))
        s.append(T(X_(a) + (-6 if a <= b else 6), y + 18, x(a), 11.5, 700, LATE if a < ON["ltvcac"] else NAVY, "end" if a <= b else "start"))
        s.append(T(X_(b) + (6 if b >= a else -6), y + 18, x(b), 11.5, 700, NAVY if b > ON["ltvcac"] else LATE, "start" if b >= a else "end"))
    yb = 28 + k * 28
    s.append(f'<line x1="{X_(ON["ltvcac"])}" y1="22" x2="{X_(ON["ltvcac"])}" y2="{yb}" stroke="{INK}" stroke-width="1.6" stroke-dasharray="4 3"/>')
    s.append(T(X_(ON["ltvcac"]), yb + 15, f"plan {ON['ltvcac']:.2f}×", 11.5, 700, INK, "middle"))
    return svg(W, yb + 22, "".join(s))


def p_tornado(n):
    rest = OAT.iloc[10:]
    small = int((abs(rest["on_hi"] - rest["on_lo"]) < 0.2).sum())
    hf = eff("hlth_family_takeup")
    c_ = eff("cac")
    body = tornado_svg() + chips([
        ("Six inputs lead", "Loan size, how many apply, the cost to win and the daily amount each move LTV/CAC by about 3 turns across their ranges; the payout and how many keep saving by about 2."),
        ("Retention matters, but less than feared", "Still saving at a year (24–45%) moves LTV/CAC by about 2 turns: KYC'd users who never save still see loan offers, so revenue does not fall as fast as savers do."),
        (f"{small} of the other {len(rest)} inputs barely matter", f"Each moves LTV/CAC by under 0.2×; every insurance, product and card assumption is among them (family health cover is the largest, {abs(hf[1] - hf[0]):.2f}×). The full list is on the workbook's 'What moves it' tab.")])
    return page(n, "What moves it", "ONE INPUT AT A TIME", f"Six inputs each move LTV/CAC by two turns or more (the cost to win: {x(c_[1])} to {x(c_[0])}); no other input moves it by two",
                body, "Each bar: the input at each end of its tested range, every other input at the plan; the range reads in the bar's order, left to right. Online saver, first five years.")


def hist_svg(series, bins, W, title, fmt_, line=None, col=TEAL, xlab=""):
    h, e = np.histogram(series, bins=bins)
    H, x0, base = 252, 34, 200
    bw = (W - x0) / len(h)
    s = [T(0, 14, title, 11.5, 700, SLATE, ls=1.1)]
    s.append(T(x0 - 6, base + 4, "0", 10.5, 600, MUTE, "end") + T(x0 - 6, base - 160 + 4, str(int(h.max())), 10.5, 600, MUTE, "end"))
    s.append(T(W, base + 36, xlab, 11, 600, MUTE, "end"))
    for i, c in enumerate(h):
        hh = 160 * c / h.max()
        s.append(R(x0 + i * bw + 1.5, base - hh, bw - 3, hh, col if (line is None or e[i] >= line) else LATE, r=2))
        if i % 2 == 0:
            s.append(T(x0 + i * bw, base + 16, fmt_(e[i]), 10.5, 600, MUTE, "middle"))
    if line is not None:
        xl = x0 + (line - e[0]) / (e[-1] - e[0]) * (W - x0)
        s.append(f'<line x1="{xl}" y1="26" x2="{xl}" y2="{base}" stroke="{RED}" stroke-width="2" stroke-dasharray="5 4"/>' + T(xl + 6, 36, f"{line:g}×", 12, 800, RED))
    return svg(W, H, "".join(s))


def p_mc(n):
    on = MC["on_ltv60"].clip(upper=10)
    pay = MC["on_pay"].clip(upper=48)
    dl = MC["door_ltv60"]
    left = hist_svg(on, np.arange(0.5, 10.51, 0.5), 560, "ONLINE LTV/CAC, 5 YEARS: FUTURES PER BIN, OF 1,000", lambda v: f"{v:g}×", line=3, xlab="online LTV/CAC, 5 years (10× and above in the last bin)")
    right = hist_svg(pay, np.arange(8, 50, 2), 560, "ONLINE: MONTH THE SAVER PAYS BACK, FUTURES PER BIN", lambda v: f"{v:.0f}", line=None, col=NAVY4, xlab="month after the saver joins (48 and later in the last bin)")
    rows = [["Online LTV/CAC, 5 years", x(MC_P10), x(MC_P50), x(MC_P90), f"{SH3:.0%}"],
            ["Online LTV/CAC, 8 years", *(x(float(np.percentile(MC["on_ltv96"], q))) for q in (10, 50, 90)), f"{(MC['on_ltv96'] >= 3).mean():.0%}"],
            ["Online pays back in month", *(f"{np.percentile(MC['on_pay'], q):.0f}" for q in (10, 50, 90)), f"{SH24:.0%} by month 24"],
            ["Doorstep LTV/CAC, 5 years", *(x(float(np.percentile(dl, q))) for q in (10, 50, 90)), f"{(dl >= 3).mean():.0%}"],
            ["Doorstep pays back in month", *(f"{np.percentile(MC['door_pay'], q):.0f}" for q in (10, 50, 90)), f"{(MC['door_pay'] <= 24).mean():.0%} by month 24"]]
    tb = table(["", "10th percentile", "Median", "90th percentile", "Share at 3× or more"], rows, [34, 16, 16, 16, 18], 12, compact=True)
    body = two(left, right, 560) + tb
    return page(n, "1,000 futures", "MONTE CARLO · OUR OWN RANGES, NOT OBSERVED ODDS: A STRESS TEST, NOT A FORECAST",
                f"Across 1,000 simulated futures the online saver's median LTV/CAC is {x(MC_P50)}; {SH3:.0%} of futures reach 3×, and 1 in 10 falls below {x(MC_P10)}",
                body, f"{len(OAT)} inputs drawn at once from their ranges (Latin hypercube, the same 1,000 futures as the company Monte Carlo; approvals and losses move together in bad years). "
                      f"The cost to win is drawn from ₹300 to ₹600, so no future is worse than the seed's budget. The plan ({x(ON['ltvcac'])}) sits above the median because the ranges are wider on the downside. Red bars: below 3×.")


def p_true(n):
    def med(mask, col="on_ltv60"):
        return float(MC.loc[mask, col].median())
    lowapp = MC["on_apply"] < 0.2
    lowret = MC["on_r12"] < 0.3
    hicac = MC["cac"] > 525
    below3 = MC["on_ltv60"] < 3
    rows = [["Fewer than 20% apply for a loan a year", f"{lowapp.mean():.0%}", x(med(lowapp)), f"{med(lowapp, 'on_pay'):.0f}"],
            ["Fewer than 30 in 100 still saving at a year", f"{lowret.mean():.0%}", x(med(lowret)), f"{med(lowret, 'on_pay'):.0f}"],
            ["Cost to win above ₹525", f"{hicac.mean():.0%}", x(med(hicac)), f"{med(hicac, 'on_pay'):.0f}"],
            ["All 1,000 futures", "100%", x(MC_P50), f"{MC['on_pay'].median():.0f}"],
            ["Only 2% apply (the nearest observed rate), all else at the plan", "one test", x(AP2["ltvcac"]), f"{AP2['pay']}"]]
    tb = table(["In futures where…", "Share of futures", "Median online LTV/CAC", "Median payback month"], rows, [46, 16, 20, 18], 12)
    co = [["Online LTV/CAC under 3×", f"{below3.mean():.0%}", f"{MC.loc[below3, 'co_profit'].median():.0f}", f"${MC.loc[below3, 'co_money'].median():.1f}M"],
          ["Online LTV/CAC 3× or more", f"{(~below3).mean():.0%}", f"{MC.loc[~below3, 'co_profit'].median():.0f}", f"${MC.loc[~below3, 'co_money'].median():.1f}M"]]
    tb2 = table(["Same futures, the whole company (profitable path)", "Share", "Median profit month", "Median money needed"], co, [46, 16, 20, 18], 12)
    pl = [(pass_line("on_apply", 0.01, 0.35), lambda v: f"at least {v:.0%} apply for a loan a year (plan 35%)"),
          (pass_line("cac", 450, 1500), lambda v: f"a cost to win of at most {rs(round(v, -1) if v > 1000 else round(v / 5) * 5)} (plan ₹450)"),
          (pass_line("on_r12", 0.05, 0.38), lambda v: f"at least {v * 100:.0f} in 100 still saving at a year (plan 38)"),
          (pass_line("on_ticket", 10000, 100000), lambda v: f"loans of at least ₹{v / 1000:.0f},000 (plan ₹1 lakh)"),
          (pass_line("on_fee", 0.002, 0.02), lambda v: f"a payout of at least {v * 100:.2f}% (plan 2%)"),
          (pass_line("on_reach", 1, 2.5), lambda v: f"offers reaching at least {v:.1f} users per saver (plan 2.5)")]
    d50 = at(on_daily=50)["ltvcac"]
    box_ = (f'<div style="border:1.5px solid {TEAL};border-radius:12px;padding:12px 16px;font-size:12.5px;line-height:1.5">'
            f'<b style="color:{NAVY}">Where 3× holds, one input at a time</b> (everything else at the plan):<br>'
            + "<br>".join(f"· {f(v)}" for v, f in pl if v is not None)
            + f'<br>The daily amount alone cannot break it: ₹50 a day still gives {x(d50)}.'
            f'<div style="margin-top:8px;color:{SLATE}">Rules on digital lending and on referral payouts could change what lenders pay; the payout line is the one to watch.</div></div>')
    body = two(tb + '<div style="height:12px"></div>' + tb2, box_, 720) + chips([
        ("Test the loan funnel first", "How many KYC'd users apply, and how many are approved, is the least-observed and most powerful number. We plan to measure both with the seed's first lending partner."),
        ("Then retention and the cost to win", "We plan to measure both from the first cohort: cost per saver won each month, and the share still saving at months 3, 6 and 12."),
        ("Ask the workbook", "Every line here is a live question on the workbook's Projector tab; it filters the 1,000 futures by any input and reports any result.")])
    return page(n, "What has to be true", "THE TESTS THAT MATTER", f"The loan funnel decides it: below 20% applying, the median LTV/CAC is {x(med(lowapp))} ({x(AP2['ltvcac'])} at 2%); "
                f"futures under 3× push company profit from month {MC.loc[~below3, 'co_profit'].median():.0f} to {MC.loc[below3, 'co_profit'].median():.0f}", body,
                "Company: the profitable path, 20,000 online savers won a month from month 30. Money needed: the peak cash spent before profit, in $ at ₹95. Same 1,000 futures as the LTV/CAC, so each row is one consistent future.")


def p_workbook(n):
    rows = [["LTV-CAC", "The answer, live: waterfall, LTV/CAC over 5 and 8 years, payback, for both savers; the 1,000 futures' summary; next to the plan model's values (gap 0)."],
            ["Projector", "Ask the 1,000 futures anything: any result, any percentile, the share above a line, with up to three filters on any input."],
            ["Inputs", f"{len(INP)} assumptions ({len(OAT)} drawn in the Monte Carlo, {len(INP) - len(OAT)} fixed), each with its value, unit, range, source and reason; 20 worked-out values in grey."],
            ["Saver", "One saver won, months 1–96, online and doorstep: still saving, deposits, balance, each revenue line, serving, cumulative after the cost to win."],
            ["Engine, Products", "The month-by-month machinery: the fund, first, repeat and top-up loans, cards, and 19 products with their renewals."],
            ["Monte Carlo, What moves it, Sources", "The 1,000 futures (values), every input one at a time with rank correlations, and the research behind each source ID."]]
    tb = table(["Tab", "What it holds"], rows, [22, 78], 13)
    body = tb + chips([
        ("Checked to the rupee", "Every formula was replayed by an independent formula engine and matches the plan's model at the plan and at five Monte Carlo futures spread from 1.9× to 7.6×: LTV/CAC to six decimals, the payback month exactly."),
        ("Live where it matters", "The one-saver model is about 13,000 live formulas: change ₹100 a day to ₹300 and LTV/CAC moves from 4.10× to 6.46× in the sheet. The 1,000 futures and the one-at-a-time tests are values, rerun on request."),
        ("Shareable", f'The workbook:<br><span style="word-break:break-all">{SHEET_URL}</span>')])
    return page(n, "The workbook", "HOW TO CHECK ANY NUMBER HERE", "Every number in this deck is a cell in the LTV/CAC workbook: change an assumption and the per-saver answer moves live", body,
                "Blue cells are assumptions; grey cells are worked out. The arithmetic is checked; the assumptions are ours. The Monte Carlo and one-at-a-time tests are rerun on request when assumptions change.")


def divider(n):
    return f"""<section class="page" style="background:{NAVY};color:#fff;display:flex;flex-direction:column;justify-content:center">
<div style="font-size:14px;letter-spacing:.18em;font-weight:700;color:#9fd8cf">APPENDIX</div>
<div style="font-size:44px;font-weight:600;margin-top:10px">Every assumption, every product, every source</div>
<div style="font-size:16px;margin-top:16px;max-width:900px;line-height:1.5;color:#dbe5f0">A1–A6 every input with its range, source and effect · A7 every product's money · A8–A10 the sources · A11 how the model works.</div>
<footer class="pf" style="color:#9fb3c8"><span>{FOOT}</span><span>{n}</span></footer></section>"""


def a_inputs(n, keys, label, j, of):
    rows = []
    for k in keys:
        g, lab, val, unit, mck, src, why, fm = INP[k]
        spec = lb.ALLSPEC.get(mck) if mck else None
        rng = f"{short_rs(spec[1], fm)} – {short_rs(spec[3], fm)}" if spec and spec[0] != "fixed" and spec[1] != spec[3] else "fixed"
        e = ""
        if mck in OAT.index:
            a, b, da, db = (float(OAT.loc[mck, c]) for c in ("on_lo", "on_hi", "door_lo", "door_hi"))
            if abs(a - b) >= 0.005:
                e = f"{a:.2f}× – {b:.2f}×"
            elif abs(da - db) >= 0.005:
                e = f"doorstep {da:.2f}× – {db:.2f}×"
            else:
                e = "no effect"
        rows.append([clip(deck_words(lab), 54), VAL_SHOW.get(k) or short_rs(val, fm), rng, e, cut(tidy(lb.clean(lb.neutral(src))), 50) or SHORT_SRC.get(k, "")])
    tb = table(["Assumption", "Value", "Range we test", "Online LTV/CAC, low → high end", "Source (in full on the workbook's Inputs tab)"], rows, [33, 9, 13, 14, 31], 10.5, compact=True)
    return page(n, "Appendix", f"{label} · EVERY ASSUMPTION ({j} OF {of})",
                f"Every input to one saver's LTV/CAC and its tested range ({j} of {of})", tb,
                "Ranges are PERT draws: a smooth hump between the low and high end, peaking at the plan's value, so most futures sit near it. Fixed = not drawn. "
                "Ends: online LTV/CAC with the input at its low and then its high end, everything else at the plan (doorstep where only the doorstep saver is affected).")


def a_products(n):
    rows = []
    for q, kind, nm, _d in ce.PRODUCTS:
        money = float(P[f"rev_xs_{q}"][0][:60].sum()) * (REACH if q.startswith("loan_") else 1)
        money96 = float(P[f"rev_xs_{q}"][0].sum()) * (REACH if q.startswith("loan_") else 1)
        group = "Other lenders' loans" if q.startswith("loan_") else ("Insurance" if q in ce.INSURANCE else "Other products")
        rows.append([lb.PRODUCT_LABEL[q] + (" (off: the core savings are the SIP)" if q == "sip" and money == 0 else ""), group, rs(money), rs(money96)])
    rows.append(["Personal + business loans (our DSA payout)", "Loans", rs(ON["pb"]), rs(ON["pb96"])])
    rows.append(["Cards", "Cards", rs(ON["cards"]), rs(ON["cards96"])])
    rows.append(["Fund trail", "Fund", rs(ON["fund"]), rs(ON["fund96"])])
    rows.append(["<b>Revenue</b>", "", f"<b>{rs(ON['rev'])}</b>", f"<b>{rs(ON['rev96'])}</b>"])
    tb = table(["Product", "Stream", "₹ per online saver won, 5 years", "8 years"], rows, [46, 20, 18, 16], 9.5, compact=True)
    return page(n, "Appendix", "A7 · EVERY PRODUCT'S MONEY", "What each product brings in from one online saver won", tb,
                "Loans count every KYC'd user reached (2.5 per online saver won). The extra equity SIP is off while the core savings are the equity SIP.")


def a_sources(n, rows, label):
    def says(r):
        c, v = str(r[1]), str(r[2]).strip()
        return c if not v or v.split(" ")[0] in c else f"{c}: <b>{v}</b>"
    tb = table(["ID", "What it says", "Source"], [[r[0], clip(tidy(says(r)), 112), clip(tidy(r[3]), 34)] for r in rows], [7, 68, 25], 9.5, compact=True, extra="oneline")
    return page(n, "Appendix", f"{label} · SOURCES · LINKS AND NOTES FOR EACH ID ON THE WORKBOOK'S SOURCES TAB", "The research behind the assumptions", tb)


def a_method(n):
    rows = [["Who keeps saving", "A steady monthly drop-off within months 1–3, another within months 4–12 (set by the share at month 3 and at month 12), then 1.5% a month."],
            ["The fund", "Balance = last month's balance less 1% withdrawn, plus deposits, plus the blended return on both. Our trail = average balance × 0.67% ÷ 12."],
            ["Loans", "Each reachable user is in one of three states: never borrowed, repaid and able to borrow again, or repaying. Each month a share applies (35% a year spread over 12 months, × the take-up factor); approved first loans move to repaying; 18 months later they can borrow again."],
            ["Top-ups", "Borrowers with 12+ EMIs paid and EMIs still due: 15% a year take a top-up of 40% of the original loan, at most one per loan."],
            ["Payouts", "Money lent × the payout (2% rising in a straight line to 3% by month 60) × (1 − 2.5% taken back). Counted for 2.5 KYC'd users per online saver."],
            ["Products", "For each product, the share not yet holding it buys at a monthly rate (the yearly take-up spread over 12 months × the take-up factor). Policies renew yearly at their renewal rate; habits keep running; insurance pays the partner's share."],
            ["Factors", "Take-up factor: 50% in months 1–6, then 100%, × 1.05 per business year to year 5 (cap 2×). First-loan approval: 30% × 60% in months 1–6 × 1.10 per year (cap 80%)."],
            ["Serving and payback", "Serving = (₹5 + ₹1) × share still saving. Cumulative = −cost to win + Σ(revenue − serving); pays back in the first month it reaches zero."]]
    tb = table(["Step", "How it is worked out, every month"], rows, [18, 82], 12)
    return page(n, "Appendix", "A11 · HOW THE MODEL WORKS", "The month-by-month rules behind one saver's value", tb,
                "These are the rules on the workbook's Engine, Products and Saver tabs, one column each.")


def build():
    pages = [cover()]
    story = [p_how, p_answer, p_payback, p_cac, p_retention, p_saving, p_fund, p_loans_reach, p_loans_pb, p_loans_other, p_products, p_serve,
             p_tornado, p_mc, p_true, p_workbook]
    for i, f in enumerate(story, start=2):
        pages.append(f(i))
    k = len(pages) + 1
    pages.append(divider(k))
    keys = list(INP)
    for j, part in enumerate(np.array_split(np.array(keys, dtype=object), 6)):
        pages.append(a_inputs(k + 1 + j, list(part), f"A{j + 1}", j + 1, 6))
    pages.append(a_products(k + 7))
    text = " ".join(str(v) for v in INP.values())
    src_tab, _missing = lb.sources_tab(text)
    srows = src_tab["_data"]
    per_s = (len(srows) + 2) // 3
    for j in range(3):
        pages.append(a_sources(k + 8 + j, srows[j * per_s:(j + 1) * per_s], f"A{8 + j}"))
    pages.append(a_method(k + 11))
    css = sp.CSS + (".at.compact td { padding: 2.5px 8px; } .at.compact th { padding: 3px 8px; }"
                    ".at.oneline { table-layout: fixed; width: 100%; } .at.oneline td { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }"
                    ".chips3 { margin-top: 8px !important; gap: 14px; } .chip { font-size: 12px; padding: 9px 14px; line-height: 1.36; } .chip b { font-size: 13px; }")
    html = f'<!doctype html><html><head><meta charset="utf-8"><title>LTV/CAC deck</title><style>{css}</style></head><body>{"".join(pages)}</body></html>'
    for a_, b_ in (("Bachatt conversation", "Conversation with a daily-savings app"), ("Bachatt minimum", "a daily-savings app's minimum"),
                   ("Bachatt film", "that app's film"), ("Bachatt's partners", "a daily-savings app's partners"), ("Bachatt homepage", "A daily-savings app's homepage"),
                   ("Bachatt acts", "The app acts"), ("Bachatt", "a daily-savings app")):
        html = html.replace(a_, b_)
    html = deck_words(html)
    for bad in ("Bueno", "BetterPlace", "Bachatt", "Saket", "Arvinder", ".py", ".csv", "tables/"):
        assert bad.lower() not in re.sub(r"<[^>]+>", " ", html).lower(), bad
    assert not re.search(r"\b(he|his|him|she|her)\b", re.sub(r"<[^>]+>", " ", html)), "gendered word"
    out = HERE / "LTV_CAC_deck.html"
    out.write_text(html)
    pdf = HERE / "LTV_CAC_deck.pdf"
    subprocess.run([sp.CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", out.as_uri()], check=True, capture_output=True)
    print("wrote", pdf, len(pages), "pages")


if __name__ == "__main__":
    build()

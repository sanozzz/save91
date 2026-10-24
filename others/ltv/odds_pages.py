"""The LTV/CAC Monte Carlo pages, shared by the LTV/CAC deck (ltv/build_ltv_simple.py) and the business case
(online/build_online_case.py): the odds, what proving each input buys, the company at each LTV/CAC (the ladder) and the main
case's financials. Numbers: tables/ltv_odds_*.csv and ltv_ladder*.csv (model/ltv_odds.py). Each page function returns
(kicker, title, body, source); the deck puts it in its own page frame."""
import numpy as np
import pandas as pd

import build_ltv_deck as ld
import ltv_odds as lo

op, sp = ld.op, ld.sp
T, R, svg, chips, two, table = ld.T, ld.R, ld.svg, ld.chips, ld.two, ld.table
INK, NAVY, TEAL, AMBER, SLATE, LINE, LATE = ld.INK, ld.NAVY, ld.TEAL, ld.AMBER, ld.SLATE, ld.LINE, ld.LATE
rs, pct, x = ld.rs, ld.pct, ld.x
MID = "#9fb3c8"                                   # pays back, below 3x

DRAWS = pd.read_csv(ld.TAB / "ltv_odds_draws.csv")
DRV = pd.read_csv(ld.TAB / "ltv_odds_drivers.csv").set_index("input")
LAD = pd.read_csv(ld.TAB / "ltv_ladder.csv").set_index("rung")
LADY = pd.read_csv(ld.TAB / "ltv_ladder_yearly.csv")
L = DRAWS["ltv_cac"]
MED, P1, P3 = float(L.median()), float((L >= 1).mean()), float((L >= 3).mean())
XMED = f"{MED:.2f}×"          # the main case to two decimals: the live sheet's own 1.7515 and the model's 1.7495 both read 1.75
MAIN, TOP = LAD.loc["Median"], LAD.loc["Our targets"]
T_MAIN = float(MAIN["position (0 market, 1 targets)"])
CAC = op.CAC * (1 + op.CONTINGENCY)
N_IN = len(lo.INPUTS)
assert abs(float(MAIN["LTV/CAC 5y"]) - MED) < 0.01, (MAIN["LTV/CAC 5y"], MED)
assert abs(float(TOP["LTV/CAC 5y"]) - ld.ON["ltvcac"]) < 0.01, (TOP["LTV/CAC 5y"], ld.ON["ltvcac"])


# where each market value comes from (reviews/2026-10-23_ltv_cac_check/evidence.md), shared with the decks' input tables
SOURCE = {"ticket": "first loans ₹5,000–25,000; digital lenders ₹15,000–1.2 lakh (bureau, FACE)",
          "apply": "1–5% of app users borrow a year (Paytm, Kissht, PhonePe filings)",
          "reach": "not measured anywhere",
          "keep": "24–45% at a year; 1–4% a month after",
          "approved": "11% of new applicants at an app lender (prospectus)",
          "rises": "no source found",
          "home_lap": "mass-market lenders ₹10–15 lakh / ₹3–10 lakh",
          "payout": "rate cards 1–2.5%, flat",
          "trail": "0.50–0.88% equity, 0.08–0.50% debt",
          "repeat": "74% of repeat customers at an app lender"}
assert set(SOURCE) == set(lo.INPUTS)


def month(m):
    m = int(m)
    return f"month {m}" if m <= 96 else "not by year 8"


def usd(v):
    return f"${float(v):.1f}M"


def cr(v):
    v = float(v)
    return f"{'−' if v < 0 else ''}₹{abs(v):,.0f} Cr" if abs(v) >= 10 else f"{'−' if v < 0 else ''}₹{abs(v):.2f} Cr"


def lakh(v):
    return f"₹{v / 1e5:.1f} lakh" if v >= 1e5 else f"₹{v / 1e3:.0f}k"


def val(k, t):
    """Input k at position t (0 = today's market, 1 = our target), in words."""
    v = {p: mk + (tg - mk) * t for p, (mk, tg) in lo.INPUTS[k][1].items()}
    if k == "ticket":
        return lakh(v["ticket"]).replace("₹3.0 lakh", "₹3 lakh")
    if k in ("apply", "approved", "repeat"):
        return pct(v.get("_apply", v.get("approved_first", v.get("approved_repeat"))))
    if k == "reach":
        return "savers only" if v["_loan_reach"] <= 1.0001 else f"{v['_loan_reach'] - 1:.1f} more per saver"
    if k == "rises":
        return "none" if t == 0 else f"+{v['takeup_growth']:.1%} and +{v['approval_growth']:.0%} a year".replace(".0%", "%")
    if k == "home_lap":
        return f"₹{v['loan_home_ticket'] / 1e5:.0f} lakh / ₹{v['loan_lap_ticket'] / 1e5:.0f} lakh"
    if k == "payout":
        return "2%, flat" if t == 0 else f"2% rising to {2 * (1 + v['_payout_rise']):.1f}%".replace(".0%", "%")
    if k == "keep":
        return f"{v['r12']:.0%}, then {v['churn_late']:.1%} stop a month"
    if k == "trail":
        return pct(0.8 * op.EQ_TRAIL + 0.2 * v["_debt_trail"], 2)
    raise KeyError(k)


# ---------- the odds
def odds_svg(W=1100, H=300):
    top, bot, x0, x1, mx = 46, H - 44, 30, W - 20, 8.0
    X = lambda v: x0 + (x1 - x0) * min(v, mx) / mx
    edges = np.arange(0, mx + 0.25, 0.25)
    cnt, _ = np.histogram(np.minimum(L, mx - 1e-9), bins=edges)
    Y = lambda c: bot - (bot - top - 14) * c / cnt.max()
    out = []
    for i, c in enumerate(cnt):
        mid = edges[i] + 0.125
        col = LATE if mid < 1 else (MID if mid < 3 else TEAL)
        out.append(R(X(edges[i]) + 1, Y(c), X(0.25) - X(0) - 2, bot - Y(c), col, r=2))
    out.append(f'<line x1="{x0}" y1="{bot}" x2="{x1}" y2="{bot}" stroke="{INK}" stroke-width="1.2"/>')
    for v in range(0, 9):
        out.append(T(X(v), bot + 18, f"{v}×", 11.5, 600, SLATE, "middle"))
    out.append(T(x1, bot + 36, "online LTV/CAC over five years, 1,000 what-ifs", 11.5, 600, SLATE, "end"))
    for v, lab, col, dash in ((MED, f"median {XMED}", NAVY, ""), (3.0, "3×", SLATE, ' stroke-dasharray="4 4"')):
        out.append(f'<line x1="{X(v):.1f}" y1="{top - 6}" x2="{X(v):.1f}" y2="{bot}" stroke="{col}" stroke-width="2"{dash}/>')
        out.append(T(X(v) + 6, top + 4, lab, 13, 800, col))
    tv = float(TOP["LTV/CAC 5y"])
    out.append(f'<path d="M{X(tv):.1f} {bot - 16} l8 8 l-8 8 l-8 -8 z" fill="{NAVY}"/>')
    out.append(T(X(tv) - 12, bot - 26, f"our targets, {x(tv)}: every input at its target at once", 12, 700, NAVY, "end"))
    out.append(T(X(0.5), 16, f"below 1×: {1 - P1:.0%}", 13, 800, LATE, "middle"))
    out.append(T(X(2.0), 16, f"pays back, below 3×: {P1 - P3:.0%}", 13, 800, SLATE, "middle"))
    out.append(T(X(4.2), 16, f"3× or more: {P3:.0%}", 13, 800, TEAL, "middle"))
    return svg(W, H, "".join(out))


def p_odds():
    title = (f"With the cost to win fixed at {rs(CAC)}, the median saver returns {XMED}; {P3:.0%} of the what-ifs reach 3× and "
             f"{1 - P1:.0%} do not pay back in five years")
    body = odds_svg() + chips([
        ("Cost to win is known", f"₹{op.SEED_CAC:.0f} in the seed and {rs(op.CAC)} after, measured on our own funnel, plus our 10% contingency. "
                                 "It is held fixed; only the value of a saver is drawn."),
        ("The value is not", f"Each of {N_IN} unmeasured inputs is equally likely anywhere between today's market and our target. "
                             "Loan inputs move together: savers who want credit apply more, borrow more and are approved more."),
        (f"{x(float(TOP['LTV/CAC 5y']))} is the top corner", "It needs every input at its target at the same time. None of the 1,000 what-ifs gets "
                                                            f"there; the best tenth reach {x(float(np.percentile(L, 90)))} or more.")])
    return ("THE ODDS", title, body,
            "A Monte Carlo: 1,000 random what-ifs, the loan inputs moving together. Market values: the middle of the 2024–26 evidence. "
            "LTV/CAC: revenue less serving over 60 months, divided by the cost to win; undiscounted.")


# ---------- what proving each input buys
SHORT = {"ticket": "The average loan", "reach": "Reaching users who never save", "apply": "The apply rate", "keep": "Retention"}
def prove_svg(W=1100):
    L0, x0, x1, rh = 0, 470, 1000, 33
    hi = max(0.5, float(DRV["chance >=3x if at target"].max()) + 0.05)
    X = lambda v: x0 + (x1 - x0) * v / hi
    out = [T(x0, 12, "0%", 11, 600, SLATE, "middle")]
    for v in (0.1, 0.2, 0.3, 0.4, 0.5):
        if v <= hi:
            out.append(T(X(v), 12, f"{v:.0%}", 11, 600, SLATE, "middle"))
    y = 22
    for k, r in DRV.iterrows():
        a, b = float(r["chance >=3x if at market"]), float(r["chance >=3x if at target"])
        out.append(T(L0, y + 13, lo.INPUTS[k][0], 12.5, 700, NAVY))
        out.append(T(L0, y + 27, f"market {val(k, 0)}  →  target {val(k, 1)}", 10.5, 500, SLATE))
        out.append(f'<line x1="{X(min(a, b)):.1f}" y1="{y + 14}" x2="{X(max(a, b)):.1f}" y2="{y + 14}" stroke="{LINE}" stroke-width="6" stroke-linecap="round"/>')
        out.append(f'<circle cx="{X(a):.1f}" cy="{y + 14}" r="6.5" fill="{LATE}"/><circle cx="{X(b):.1f}" cy="{y + 14}" r="6.5" fill="{TEAL}"/>')
        if b - a > 0.035:
            out.append(T(X(a) - 10, y + 19, f"{a:.0%}", 12, 800, LATE, "end") + T(X(b) + 10, y + 19, f"{b:.0%}", 12, 800, TEAL))
        else:
            out.append(T(X(max(a, b)) + 12, y + 19, f"{min(a, b):.0%}–{max(a, b):.0%}: hardly moves it", 11.5, 700, SLATE))
        y += rh
    out.append(f'<line x1="{X(P3):.1f}" y1="18" x2="{X(P3):.1f}" y2="{y}" stroke="{NAVY}" stroke-width="1.5" stroke-dasharray="4 4"/>')
    out.append(T(X(P3), y + 14, f"not yet measured: {P3:.0%}", 11.5, 700, NAVY, "middle"))
    return svg(W, y + 22, "".join(out))


def p_prove():
    d = DRV.iloc[0]
    k = DRV.index[0]
    title = (f"{SHORT.get(k, lo.INPUTS[k][0])} decides most: if it proves at {val(k, 1)} the chance of 3× rises from {P3:.0%} to "
             f"{float(d['chance >=3x if at target']):.0%}; at {val(k, 0)} it falls to {float(d['chance >=3x if at market']):.0%}")
    legend = (f'<div style="display:flex;gap:18px;font-size:12px;color:{INK};margin:0 0 4px">'
              f'<span><b style="color:{LATE}">●</b> if the seed finds today\'s market value</span>'
              f'<span><b style="color:{TEAL}">●</b> if it finds our target</span>'
              f'<span style="color:{SLATE}">chance that LTV/CAC reaches 3×; every other input still drawn</span></div>')
    return ("WHAT EACH MEASUREMENT IS WORTH", title, legend + prove_svg(),
            "The same 1,000 what-ifs with one input fixed at today's market value, then at our target. Inputs ranked by how much the median moves.")


# ---------- the ladder: the company at each LTV/CAC
def ladder_svg(W=1100):
    rows = sorted(LAD.iterrows(), key=lambda kr: -float(kr[1]["LTV/CAC 5y"]))
    mx = float(LAD["money needed $M"].max()) * 1.08
    xb0, xb1, xm, rh = 290, 560, 680, 38
    out = [T(0, 14, "LTV/CAC · CHANCE OF AT LEAST THIS", 11, 700, SLATE, ls=1), T(xb0, 14, "MONEY NEEDED IN ALL", 11, 700, SLATE, ls=1),
           T(xm, 14, "EBITDA POSITIVE FROM", 11, 700, SLATE, ls=1), T(W, 14, "YEAR 5 EBITDA · 8-YEAR TOTAL", 11, 700, SLATE, "end", ls=1)]
    y = 26
    for k, r in rows:
        main = k == "Median"
        if main:
            out.append(R(-6, y, W + 12, rh - 2, sp.NAVY_L, r=8))
        name = {"Median": "main case (median)", "Our targets": "our targets", "Today's market": "today's market"}.get(k, "")
        lv = float(r["LTV/CAC 5y"])
        col = NAVY if main else (LATE if lv < 1 - 1e-6 else (SLATE if lv < 3 - 1e-6 else TEAL))
        chance = {"Our targets": "every target at once", "Today's market": "every input at market"}.get(k, f"chance {float(r['chance of at least this']):.0%}")
        out.append(T(0, y + 23, XMED if main else x(lv), 18, 800, col) + T(62, y + 16, name, 13, 700, NAVY if main else INK)
                   + T(62, y + (30 if name else 23), chance, 11.5, 500, SLATE))
        w = (xb1 - xb0) * float(r["money needed $M"]) / mx
        ink = NAVY if main else INK
        out.append(R(xb0, y + 8, w, 20, NAVY if main else MID, r=5) + T(xb0 + w + 8, y + 23, usd(r["money needed $M"]), 13, 800, ink))
        out.append(T(xm, y + 23, month(r["EBITDA positive from month"]), 13.5, 800 if main else 700, ink))
        out.append(T(W, y + 23, f"{cr(r['Y5 EBITDA Rs cr'])} · {cr(r['cumulative EBITDA 8y Rs cr'])}", 13, 700, ink, "end"))
        y += rh
    return svg(W, y + 4, "".join(out))


def p_ladder():
    t3 = LAD.loc["3×"]
    title = (f"At the median {XMED} EBITDA turns positive in {month(MAIN['EBITDA positive from month'])} on {usd(MAIN['money needed $M'])}; "
             f"at 3×, {month(t3['EBITDA positive from month'])} on {usd(t3['money needed $M'])}; at our targets, {month(TOP['EBITDA positive from month'])} "
             f"on {usd(TOP['money needed $M'])}")
    body = ladder_svg() + chips([
        ("One plan, many outcomes", f"Every row is the same company: {lo.LEVEL:,} online savers a month from month 30, the same team and the same cost to win. "
                                    "Only the value of a saver changes."),
        ("The main case", f"Every unmeasured input {T_MAIN:.0%} of the way from today's market to our target gives the median, {XMED}. "
                          "The financials are built on it."),
        ("What the seed buys", f"Which row we are on. The next round (money needed less the $0.5M seed) is about "
                               f"{usd(float(MAIN['money needed $M']) - 0.5)} at the median and {usd(float(t3['money needed $M']) - 0.5)} at 3×.")])
    return ("THE COMPANY AT EACH LTV/CAC", title, body,
            "Each row: every unmeasured input the same share of the way from today's market to our target, solved for that LTV/CAC, and every row still "
            "scales to 20,000 savers a month. EBITDA: operating profit before tax. Chance: share of the 1,000 what-ifs at or above it. Money needed: the "
            "deepest cumulative cash hole, seed included, plus a ₹5 crore floor. Doorstep savers (1 in 10) carry the same loan inputs. Undiscounted.")


# ---------- the main case's financials
def main_inputs():
    keys = [k for k in DRV.index][:7]
    return [(lo.INPUTS[k][0], val(k, T_MAIN), val(k, 1)) for k in keys]


def ebitda_svg(y_, W=560, H=196):
    vals = [float(v) for v in y_["EBITDA Rs cr"]]
    cum = np.cumsum(vals)
    mx = max(max(abs(v) for v in vals), abs(cum).max(), 1.0)
    base, sc = 96, 74 / mx                                   # one scale for the bars and the cumulative line
    gw = (W - 30) / 8
    neg = lambda v: f"{'−' if v < 0 else ''}{abs(v):.0f}"
    out = [T(0, 14, "EBITDA (OPERATING PROFIT) BY YEAR, ₹ CRORE; CUMULATIVE DASHED", 11, 700, SLATE, ls=1),
           f'<line x1="20" y1="{base}" x2="{W}" y2="{base}" stroke="{INK}" stroke-width="1.2"/>']
    pts = [f"{30 + i * gw + (gw - 16) / 2:.1f},{base - c * sc:.1f}" for i, c in enumerate(cum)]
    out.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{NAVY}" stroke-width="2.2" stroke-dasharray="5 4"/>')
    halo = lambda t: t.replace("<text ", '<text paint-order="stroke" stroke="white" stroke-width="4" ', 1)
    for i, v in enumerate(vals):
        xx = 30 + i * gw
        h = v * sc
        out.append(R(xx, base - max(h, 0), gw - 16, max(abs(h), 1.5), TEAL if v >= 0 else LATE, r=3))
        out.append(halo(T(xx + (gw - 16) / 2, base - h - 6 if v >= 0 else base - h + 14, neg(v), 11.5, 700, TEAL if v >= 0 else LATE, "middle")))
        out.append(T(xx + (gw - 16) / 2, H - 4, f"Y{i + 1}", 11.5, 700, SLATE, "middle"))
    out.append(T(W, 36, f"cumulative by Y8: {neg(cum[-1])}", 11.5, 800, NAVY, "end"))
    return svg(W, H, "".join(out))


def p_financials():
    y_ = LADY[LADY["rung"] == "Median"].sort_values("year")
    m = MAIN
    yrs = [int(v) for v in y_["year"]]
    g = lambda c: [float(v) for v in y_[c]]
    lines = [("Active savers at year end, lakh", [v / 1e5 for v in g("active savers (end)")], "{:.1f}"),
             ("Revenue, ₹ Cr", g("Revenue Rs cr"), "{:.1f}"),
             ("  of which lender fees, personal and business loans", g("Loan marketing fees Rs cr"), "{:.1f}"),
             ("Cost to win savers, ₹ Cr", [-v for v in g("Acquisition Rs cr")], "{:.1f}"),
             ("Team and other costs, ₹ Cr", [-(a + b) for a, b in zip(g("Team Rs cr"), g("Other costs Rs cr"))], "{:.1f}"),
             ("<b>EBITDA, ₹ Cr</b>", g("EBITDA Rs cr"), "<b>{:.1f}</b>"),
             ("Cumulative EBITDA, ₹ Cr", list(np.cumsum(g("EBITDA Rs cr"))), "{:.1f}")]
    rows = [[lab] + [f.replace(".1f", ".2f" if "Cr" in lab else ".1f").format(v).replace("-", "−") for v in vs] for lab, vs, f in lines]
    tb = table([""] + [f"Y{y}" for y in yrs], rows, [32] + [68 / 8] * 8, 11.5, compact=True)
    ins = "".join(f'<tr><td>{a}</td><td><b>{b}</b></td><td style="color:{SLATE}">{c}</td></tr>' for a, b, c in main_inputs())
    box = (f'<div style="font-size:11px;font-weight:700;letter-spacing:1px;color:{SLATE};margin-bottom:4px">THE MAIN CASE\'S INPUTS, OUR TARGET IN GREY</div>'
           f'<table class="at compact" style="font-size:11px"><colgroup><col style="width:46%"><col style="width:28%"><col style="width:26%"></colgroup>{ins}</table>')
    body = two(ebitda_svg(y_), box, 560) + f'<div style="margin-top:14px">{tb}</div>'
    title = (f"The main case, {XMED}: EBITDA turns positive in {month(m['EBITDA positive from month'])}, the company needs {usd(m['money needed $M'])} "
             f"in all, and 8 years add up to {cr(m['cumulative EBITDA 8y Rs cr'])}")
    return ("THE FINANCIALS", title, body,
            f"{lo.LEVEL:,} online savers a month from month 30 after the seed, 1 in 10 from the doorstep; cost to win ₹{op.SEED_CAC:.0f} in the seed and "
            f"{rs(op.CAC)} after. Doorstep savers carry the same loan inputs as online savers. Team and other costs include the 10% contingency. "
            "Undiscounted; tax on profit after losses carried forward.")
